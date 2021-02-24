-- -- Script to manage authentication and some basic authorization for CHORD
-- -- services under an OpenResty (or similarly configured NGINX) instance.

-- -- Note: Many things are cached locally; this is considered good practice in
-- --       the context of OpenResty given that non-local variable access is quite
-- --       slow. This includes ngx, require, table accesses, etc.

-- local ngx = ngx
-- local require = require

-- local cjson = require("cjson")
-- local openidc = require("resty.openidc")

-- local uncached_response = function (status, mime, message)
--   -- Helper method to return uncached responses directly from the proxy without
--   -- needing an underlying service.
--   ngx.status = status
--   ngx.header["Content-Type"] = mime
--   ngx.header["Cache-Control"] = "no-store"
--   ngx.header["Pragma"] = "no-cache"  -- Backwards-compatibility for no-cache
--   ngx.say(message)
--   ngx.exit(status)
-- end

-- local OIDC_CALLBACK_PATH_NO_SLASH = "api/auth/callback"
-- local OIDC_CALLBACK_PATH = "/" .. OIDC_CALLBACK_PATH_NO_SLASH
-- local SIGN_IN_PATH = "/api/auth/sign-in"
-- local SIGN_OUT_PATH = "/api/auth/sign-out"
-- local USER_INFO_PATH = "/api/auth/user"

-- -- Load auth configuration for setting up lua-resty-oidconnect
-- local auth_file = assert(io.open("/usr/local/openresty/nginx/auth_config.json"))
-- local auth_params = cjson.decode(auth_file:read("*all"))
-- auth_file:close()

-- local config_file = assert(io.open("/usr/local/openresty/nginx/instance_config.json"))
-- local config_params = cjson.decode(config_file:read("*all"))
-- config_file:close()

-- local auth__owner_ids = auth_params["OWNER_IDS"]
-- if auth__owner_ids == nil then
--   auth__owner_ids = {}
-- end

-- -- TODO: This should probably be procedural instead of a function?
-- local get_user_role = function (user_id)
--   user_role = "user"
--   for _, owner_id in ipairs(auth__owner_ids) do
--     -- Check each owner ID set in the auth params; if the current user's ID
--     -- matches one, set the user's role to "owner".
--     if owner_id == user_id then user_role = "owner" end
--   end
--   return user_role
-- end

-- -- Set defaults for any possibly-unspecified configuration options, including
-- -- some boolean casts

-- local chord_debug = not (not config_params["CHORD_DEBUG"])

-- -- Cannot use "or" shortcut, otherwise would always be true
-- local chord_permissions = config_params["CHORD_PERMISSIONS"]
-- if chord_permissions == nil then chord_permissions = true end

-- local chord_private_mode = not (not config_params["CHORD_PRIVATE_MODE"])

-- -- If in production, validate the SSL certificate if HTTPS is being used (for
-- -- non-Lua folks, this is a ternary - ssl_verify = !chord_debug)
-- local opts_ssl_verify = "no"
-- --chord_debug and "no" or "yes"

-- -- If in production, enforce CHORD_URL as the base for redirect
-- local opts_redirect_uri = OIDC_CALLBACK_PATH
-- local opts_redirect_after_logout_uri = "/"
-- if not chord_debug then
--   opts_redirect_uri = config_params["CHORD_URL"] .. OIDC_CALLBACK_PATH_NO_SLASH
--   opts_redirect_after_logout_uri = config_params["CHORD_URL"]
-- end

-- local opts = {
--   redirect_uri = opts_redirect_uri,
--   logout_path = SIGN_OUT_PATH,
--   redirect_after_logout_uri = opts_redirect_after_logout_uri,

--   discovery = auth_params["OIDC_DISCOVERY_URI"],

--   client_id = auth_params["CLIENT_ID"],
--   client_secret = auth_params["CLIENT_SECRET"],

--   -- Default token_endpoint_auth_method to client_secret_basic
--   token_endpoint_auth_method = auth_params["TOKEN_ENDPOINT_AUTH_METHOD"] or "client_secret_basic",

--   accept_none_alg = false,
--   accept_unsupported_alg = false,
--   ssl_verify = opts_ssl_verify,

--   -- Disable keepalive to try to prevent some "lost access token" issues with the OP
--   -- See https://github.com/zmartzone/lua-resty-openidc/pull/307 for details
--   keepalive = "no",

--   -- TODO: Re-enable this if it doesn't cause sign-out bugs, since it's more secure
--   -- refresh_session_interval = 600,
--   iat_slack = 120,
-- }

-- -- Cache commonly-used ngx.var.uri to save expensive access call
-- local ngx_var_uri = ngx.var.uri or ""

-- -- Track if the current request is to an API
-- local is_api_uri = string.find(ngx_var_uri, "^/api")

-- -- Private URIs don't exist if the CHORD_PERMISSIONS flag is off (for dev)
-- -- All URIs are effectively "private" externally for CHORD_PRIVATE_MODE nodes
-- local is_private_uri = chord_permissions and (
--   (chord_private_mode and not string.find(ngx_var_uri, "^/api/auth")) or
--   string.find(ngx_var_uri, "^/api/%a[%w-_]*/private")
-- )


-- -- Calculate auth_mode for authenticate() calls,
-- -- defining the redirect/return behaviour for the OIDC library
-- --  - "pass" --> keep going, but not with any auth headers set
-- --  - "deny" --> return 401
-- --  - nil    --> return 302 to sign-in page
-- --           --> always the case if the path requested is SIGN_IN
-- local auth_mode = nil
-- print(ngx_var_uri)
-- if ngx_var_uri and ngx_var_uri ~= SIGN_IN_PATH then
--   if is_private_uri then
--     -- require authentication at the auth endpoint or in the private namespace
--     -- (or if we're in private mode)
--     if is_api_uri then
--       -- We don't want to return any 302 redirects if we're accessing an
--       -- endpoint that needs re-authorization, so deny in this case
--       auth_mode = "deny"
--     end
--     -- else: If we're not authenticated, redirect to the OP (leave as nil)
--   else
--     auth_mode = "pass"  -- otherwise pass
--   end
-- end


-- -- Need to rewrite target URI for authenticate if we're in a sub-folder
-- local auth_target_uri = ngx.var.request_uri
-- if ngx_var_uri == OIDC_CALLBACK_PATH or auth_mode == nil then
--   -- Going to attempt a redirect; possibly dealing with the OpenIDC callback
--   local after_chord_url = ngx_var_uri:match("^/(.*)")
--   if after_chord_url then
--     -- If after_chord_url is not nil, i.e. ngx var uri starts with a /
--     -- Re-assemble target URI with external URI prefixes/hosts/whatnot:
--     auth_target_uri = config_params["CHORD_URL"] .. after_chord_url  .. "?" .. (ngx.var.args or "")
--   end
-- end

-- local user
-- local user_id
-- local user_role
-- local nested_auth_header

-- -- Check bearer token if set
-- -- Adapted from https://github.com/zmartzone/lua-resty-openidc/issues/266#issuecomment-542771402
-- local auth_header = ngx.req.get_headers()["Authorization"]
-- if is_private_uri and auth_header and string.find(auth_header, "^Bearer ") then
--   -- A Bearer auth header is set, use it instead of session through introspection
--   -- For some reason, needs to be client_secret_post for Compute Canada at least:
--   -- TODO: Ideally this should be somewhat consistent...
--   -- opts.token_endpoint_auth_method = TOKEN_ENDPOINT_AUTH_POST
--   local res, err = openidc.introspect(opts)
--   -- opts.token_endpoint_auth_method = TOKEN_ENDPOINT_AUTH_BASIC
--   if err == nil and res.active then
--     -- If we have a valid access token, try to get the user info
--     user, err = openidc.call_userinfo_endpoint(
--       opts,
--       -- Slice out the access token from the Authorization header
--       auth_header:sub(auth_header:find(" ") + 1)
--     )
--     if err == nil then
--       -- User profile fetch was successful, grab the values
--       user_id = user.sub
--       user_role = get_user_role(user_id)
--       nested_auth_header = auth_header
--     end
--   end

--   if err then
--     -- Log any errors that occurred above
--     ngx.log(ngx.ERR, err)
--   end
-- else
--   -- If no Bearer token is set, use session cookie to get authentication information
--   local res, err, _, session = openidc.authenticate(
--     opts, auth_target_uri, auth_mode)
--   if res == nil or err then  -- Authentication wasn't successful
--     -- Authentication wasn't successful; clear the session and
--     -- re-attempting (for a maximum of 2 times.)
--     if session ~= nil then
--       if session.data.user_id ~= nil then
--         -- Destroy the current session if it exists and just expired
--         session:destroy()
--       elseif err then
--         -- Close the current session before returning an error message
--         session:close()
--       end
--     end
--     if err then
--       uncached_response(
--         ngx.HTTP_INTERNAL_SERVER_ERROR,
--         "application/json",
--         cjson.encode({message=err, tag="no bearer, authenticate", user_role=nil})
--       )
--     end
--   end

--   -- If authenticate hasn't rejected us above but it's "open", i.e.
--   -- non-authenticated users can see the page, clear X-User and
--   -- X-User-Role by setting the value to nil.
--   if res ~= nil then  -- Authentication worked
--     if session.data.user_id ~= nil then
--       -- Load user_id and user_role from session if available
--       user_id = session.data.user_id
--       user_role = session.data.user_role
--       -- Close the session, since we're done loading data from it
--       session:close()
--     else
--       -- Save user_id and user_role into session for future use
--       user_id = res.id_token.sub
--       user_role = get_user_role(user_id)
--       session.data.user_id = user_id
--       session.data.user_role = user_role
--       session:save()
--     end

--     -- Set user object for possible /api/auth/user response
--     user = res.user

--     -- Set Bearer header for nested requests
--     --  - First tries to use session-derived access token; if it's unset,
--     --    try using the response access token.
--     -- TODO: Maybe only res token needed?
--     local auth_token = res.access_token
--     if auth_token == nil then
--       local auth_token, err = openidc.access_token()  -- TODO: Remove this block?
--       if err ~= nil then
--         ngx.log(ngx.ERR, err)
--       end
--     end
--     if auth_token ~= nil then
--       nested_auth_header = "Bearer " .. auth_token
--     end
--   elseif session ~= nil then
--     -- Close the session, since we don't need it anymore
--     session:close()
--   end
-- end

-- -- Either authenticated or not, so from hereon out we:
-- --  - Handle scripted virtual endpoints (user info, )
-- --  - Check access given the URL
-- --  - Set proxy-internal headers

-- if ngx_var_uri == USER_INFO_PATH then
--   -- Endpoint: /api/auth/user
--   --   Generates a JSON response with user data if the user is authenticated;
--   --   otherwise returns a 403 Forbidden error.
--   if user == nil then
--     local forbidden_response = {message="Forbidden", tag="user nil", user_role=nil}
--     uncached_response(ngx.HTTP_FORBIDDEN, "application/json", cjson.encode(forbidden_response))
--   else
--     user["chord_user_role"] = user_role
--     uncached_response(ngx.HTTP_OK, "application/json", cjson.encode(user))
--   end
-- elseif ngx_var_uri == SIGN_IN_PATH then
--   -- Endpoint: /api/auth/sign-in
--   --   - If the user has not signed in, this will get caught above by the
--   --     authenticate() call;
--   --   - If the user just signed in and was redirected here, check the args for
--   --     a redirect parameter and return a redirect if necessary.
--   -- TODO: Do the same for sign-out (in certain cases)
--   local args, args_error = ngx.req.get_uri_args()
--   if args_error == nil then
--     local redirect = args.redirect
--     if redirect and type(redirect) ~= "table" then
--       ngx.redirect(redirect)
--     end
--   end
-- elseif is_private_uri and user_role ~= "owner" then
--   -- Check owner status before allowing through the proxy
--   -- TODO: Check ownership / grants?
--   local forbidden_response = {message="Forbidden", tag="user not owner", user_role=user_role}
--   uncached_response(ngx.HTTP_FORBIDDEN, "application/json", cjson.encode(forbidden_response))
-- end

-- -- Clear and possibly set internal headers to inform services of user identity
-- -- and their basic role/permissions set (either the node's owner or a user of
-- -- another type.)
-- -- Set an X-Authorization header containing a valid Bearer token for nested
-- -- requests to other services.
-- -- TODO: Pull this from session for performance
-- ngx.req.set_header("X-User", user_id)
-- ngx.req.set_header("X-User-Role", user_role)
-- ngx.req.set_header("X-Authorization", nested_auth_header)


-- -- ngx.say('Hello World!')
-- -- ngx.exit(200)

-- Script to manage authentication and some basic authorization for CHORD
-- services under an OpenResty (or similarly configured NGINX) instance.

-- Note: Many things are cached locally; this is considered good practice in
--       the context of OpenResty given that non-local variable access is quite
--       slow. This includes ngx, require, table accesses, etc.

local ngx = ngx
local require = require

local cjson = require("cjson")
local openidc = require("resty.openidc")
local random = require("resty.random")
local redis = require("resty.redis")
local str = require("resty.string")

local uncached_response = function (status, mime, message)
  -- Helper method to return uncached responses directly from the proxy without
  -- needing an underlying service.
  ngx.status = status
  if mime then ngx.header["Content-Type"] = mime end
  ngx.header["Cache-Control"] = "no-store"
  ngx.header["Pragma"] = "no-cache"  -- Backwards-compatibility for no-cache
  if message then ngx.say(message) end
  ngx.exit(status)
end

local invalidate_ott = function (redis_conn, token)
  -- Helper method to invalidate a one-time token, given a connection to the
  -- Redis instance being used and the token in question
  redis_conn:hdel("bento_ott:expiry", token)
  redis_conn:hdel("bento_ott:scope", token)
  redis_conn:hdel("bento_ott:user", token)
  redis_conn:hdel("bento_ott:user_id", token)
  redis_conn:hdel("bento_ott:user_role", token)
end

local OIDC_CALLBACK_PATH = "/api/auth/callback"
local OIDC_CALLBACK_PATH_NO_SLASH = OIDC_CALLBACK_PATH:sub(2, #OIDC_CALLBACK_PATH)
local SIGN_IN_PATH = "/api/auth/sign-in"
local SIGN_OUT_PATH = "/api/auth/sign-out"
local USER_INFO_PATH = "/api/auth/user"

local ONE_TIME_TOKENS_GENERATE_PATH = "/api/auth/ott/generate"
local ONE_TIME_TOKENS_INVALIDATE_PATH = "/api/auth/ott/invalidate"
local ONE_TIME_TOKENS_INVALIDATE_ALL_PATH = "/api/auth/ott/invalidate_all"

local REDIS_SOCKET = "unix:/chord/tmp/redis.sock"

-- Create an un-connected Redis object
local red_ok
local red, red_err = redis:new()
if red_err then
  uncached_response(
    ngx.HTTP_INTERNAL_SERVER_ERROR,
    "application/json",
    cjson.encode({message=red_err, tag="ott redis conn", user_role=nil}))
end

-- Load auth configuration for setting up lua-resty-oidconnect
local auth_file = assert(io.open("/usr/local/openresty/nginx/auth_config.json"))
local auth_params = cjson.decode(auth_file:read("*all"))
auth_file:close()

local config_file = assert(io.open("/usr/local/openresty/nginx/instance_config.json"))
local config_params = cjson.decode(config_file:read("*all"))
config_file:close()

local auth__owner_ids = auth_params["OWNER_IDS"]
if auth__owner_ids == nil then
  auth__owner_ids = {}
end

-- TODO: This should probably be procedural instead of a function?
local get_user_role = function (user_id)
  user_role = "user"
  for _, owner_id in ipairs(auth__owner_ids) do
    -- Check each owner ID set in the auth params; if the current user's ID
    -- matches one, set the user's role to "owner".
    if owner_id == user_id then user_role = "owner" end
  end
  return user_role
end

local NGX_NULL = ngx.null
local ngx_null_to_nil = function (v)
  if v == NGX_NULL then return nil else return v end
end

-- Set defaults for any possibly-unspecified configuration options, including
-- some boolean casts

local CHORD_DEBUG = not (not config_params["CHORD_DEBUG"])

-- Cannot use "or" shortcut, otherwise would always be true
local CHORD_PERMISSIONS = config_params["CHORD_PERMISSIONS"]
if CHORD_PERMISSIONS == nil then CHORD_PERMISSIONS = true end

local CHORD_PRIVATE_MODE = not (not config_params["CHORD_PRIVATE_MODE"])

-- If in production, validate the SSL certificate if HTTPS is being used (for
-- non-Lua folks, this is a ternary - ssl_verify = !chord_debug)
local opts_ssl_verify = "no"
-- CHORD_DEBUG and "no" or "yes"

-- If in production, enforce CHORD_URL as the base for redirect
local opts_redirect_uri = OIDC_CALLBACK_PATH
local opts_redirect_after_logout_uri = "/"
if not CHORD_DEBUG then
  opts_redirect_uri = config_params["CHORD_URL"] .. OIDC_CALLBACK_PATH_NO_SLASH
  opts_redirect_after_logout_uri = config_params["CHORD_URL"]
end

local opts = {
  redirect_uri = opts_redirect_uri,
  logout_path = SIGN_OUT_PATH,
  redirect_after_logout_uri = opts_redirect_after_logout_uri,

  discovery = auth_params["OIDC_DISCOVERY_URI"],

  client_id = auth_params["CLIENT_ID"],
  client_secret = auth_params["CLIENT_SECRET"],

  -- Default token_endpoint_auth_method to client_secret_basic
  token_endpoint_auth_method = auth_params["TOKEN_ENDPOINT_AUTH_METHOD"] or "client_secret_basic",

  accept_none_alg = false,
  accept_unsupported_alg = false,
  ssl_verify = opts_ssl_verify,

  -- Disable keepalive to try to prevent some "lost access token" issues with the OP
  -- See https://github.com/zmartzone/lua-resty-openidc/pull/307 for details
  keepalive = "no",

  -- TODO: Re-enable this if it doesn't cause sign-out bugs, since it's more secure
  -- refresh_session_interval = 600,

  iat_slack = 120,
  -- access_token_expires_in should be shorter than $session_cookie_lifetime otherwise will never be called:
  access_token_expires_in = 900,
  access_token_expires_leeway = 60,
  renew_access_token_on_expiry = true,
}

-- Cache commonly-used ngx.var.uri and ngx.var.request_method to save expensive access calls
local URI = ngx.var.uri or ""
local REQUEST_METHOD = ngx.var.request_method or "GET"

-- Track if the current request is to an API
local is_api_uri = not (not URI:match("^/api"))

-- Private URIs don't exist if the CHORD_PERMISSIONS flag is off (for dev)
-- All URIs are effectively "private" externally for CHORD_PRIVATE_MODE nodes
local is_private_uri = CHORD_PERMISSIONS and (
  (CHORD_PRIVATE_MODE and not URI:match("^/api/auth")) or
  URI:match("^/api/%a[%w-_]*/private"))


-- Calculate auth_mode for authenticate() calls,
-- defining the redirect/return behaviour for the OIDC library
--  - "pass" --> keep going, but not with any auth headers set
--  - "deny" --> return 401
--  - nil    --> return 302 to sign-in page
--           --> always the case if the path requested is SIGN_IN
local auth_mode
if URI and URI ~= SIGN_IN_PATH then
  if is_private_uri then
    -- require authentication at the auth endpoint or in the private namespace
    -- (or if we're in private mode)
    if is_api_uri then
      -- We don't want to return any 302 redirects if we're accessing an
      -- endpoint that needs re-authorization, so deny in this case
      auth_mode = "deny"
    end
    -- else: If we're not authenticated, redirect to the OP (leave as nil)
  else
    auth_mode = "pass"  -- otherwise pass
  end
end


-- Need to rewrite target URI for authenticate if we're in a sub-folder
local auth_target_uri = ngx.var.request_uri
if URI == OIDC_CALLBACK_PATH or auth_mode == nil then
  -- Going to attempt a redirect; possibly dealing with the OpenIDC callback
  local after_chord_url = URI:match("^/(.*)")
  if after_chord_url then
    -- If after_chord_url is not nil, i.e. ngx var uri starts with a /
    -- Re-assemble target URI with external URI prefixes/hosts/whatnot:
    auth_target_uri = config_params["CHORD_URL"] .. after_chord_url  .. "?" .. (ngx.var.args or "")
  end
end

local user
local user_id
local user_role
local nested_auth_header

local err_user_not_owner = function ()
  uncached_response(ngx.HTTP_FORBIDDEN, "application/json",
    cjson.encode({message="Forbidden", tag="user not owner", user_role=user_role}))
end
local err_user_nil = function ()
  uncached_response(ngx.HTTP_FORBIDDEN, "application/json",
    cjson.encode({message="Forbidden", tag="user is nil", user_role=user_role}))
end
local err_invalid_req_body = function ()
  uncached_response(ngx.HTTP_BAD_REQUEST, "application/json",
    cjson.encode({message="Missing or invalid body", tag="invalid body", user_role=user_role}))
end
local err_redis = function(tag)
  uncached_response(ngx.HTTP_INTERNAL_SERVER_ERROR, "application/json",
      cjson.encode({message=red_err, tag=tag, user_role=user_role}))
end
local err_invalid_method = function()
  uncached_response(ngx.HTTP_NOT_ALLOWED, "application/json",
      cjson.encode({message="Method not allowed", tag="invalid method", user_role=user_role}))
end


local req_headers = ngx.req.get_headers()

-- TODO: OTT headers are technically also a Bearer token (of a different nature)... should be combined
local ott_header = req_headers["X-OTT"]
if ott_header and not URI:match("^/api/auth") then
  -- Cannot use a one-time token to bootstrap generation of more one-time
  -- tokens or invalidate existing ones
  -- URIs do not include URL parameters, so this is safe from non-exact matches

  -- The auth namespace check should theoretically be handled by the scope
  -- validation anyway, but manually check it as a last resort

  red_ok, red_err = red:connect(REDIS_SOCKET)
  if red_err then  -- Error occurred while connecting to Redis
    err_redis("redis conn")
    goto script_end
  end

  -- TODO: Error handling for each command? Maybe overkill

  -- Fetch all token data from the Redis store and subsequently delete it
  local expiry = tonumber(red:hget("bento_ott:expiry", ott_header), 10) or nil
  local scope = ngx_null_to_nil(red:hget("bento_ott:scope", ott_header))
  user = cjson.decode(ngx_null_to_nil(red:hget("bento_ott:user", ott_header)) or "{}")
  user_id = ngx_null_to_nil(red:hget("bento_ott:user_id", ott_header))
  user_role = ngx_null_to_nil(red:hget("bento_ott:user_role", ott_header))

  red:init_pipeline(5)
  invalidate_ott(red, ott_header)  -- 5 pipeline actions
  red:commit_pipeline()

  -- Update NGINX time (which is cached)
  -- This is slow, so OTTs should not be over-used in situations where there's
  -- a more performant way that likely makes more sense anyway.
  ngx.update_time()

  -- Check token validity
  if expiry == nil then
    -- Token cannot be found in the Redis store
    uncached_response(ngx.HTTP_FORBIDDEN, "application/json",
      cjson.encode({message="Invalid one-time token", tag="ott invalid", user_role=nil}))
  elseif expiry < ngx.time() then
    -- Token expiry date is in the past, so it is no longer valid
    uncached_response(ngx.HTTP_FORBIDDEN, "application/json",
      cjson.encode({message="Expired one-time token", tag="ott expired", user_role=nil}))
  elseif URI:sub(1, #scope) ~= scope then
    -- Invalid call made with the token (out of scope)
    -- We're harsh here and still delete the token out of security concerns
    uncached_response(ngx.HTTP_FORBIDDEN, "application/json",
      cjson.encode({message="Out-of-scope one-time token", tag="ott out of scope", user_role=nil}))
  end

  -- No nested auth header is set; OTTs cannot be used to bootstrap a full bearer token

  -- Put Redis connection into a keepalive pool for 30 seconds
  red_ok, red_err = red:set_keepalive(30000, 100)
  if red_err then
    err_redis("redis keepalive failed")
    goto script_end
  end
else
  -- Check bearer token if set
  -- Adapted from https://github.com/zmartzone/lua-resty-openidc/issues/266#issuecomment-542771402
  local auth_header = ngx.req.get_headers()["Authorization"]
  if is_private_uri and auth_header and auth_header:match("^Bearer .+") then
    -- A Bearer auth header is set, use it instead of session through introspection
    local res, err = openidc.introspect(opts)
    if err == nil and res.active then
      -- If we have a valid access token, try to get the user info
      --   - Slice out the token from the Authorization header
      user, err = openidc.call_userinfo_endpoint(
        opts, auth_header:sub(auth_header:find(" ") + 1))
      if err == nil then
        -- User profile fetch was successful, grab the values
        user_id = user.sub
        user_role = get_user_role(user_id)
        nested_auth_header = auth_header
      end
    end

    -- Log any errors that occurred above
    if err then ngx.log(ngx.ERR, err) end
  else
    -- If no Bearer token is set, use session cookie to get authentication information
    local res, err, _, session = openidc.authenticate(
      opts, auth_target_uri, auth_mode)
    if res == nil or err then  -- Authentication wasn't successful
      -- Authentication wasn't successful; clear the session and
      -- re-attempting (for a maximum of 2 times.)
      if session ~= nil then
        if session.data.user_id ~= nil then
          -- Destroy the current session if it exists and just expired
          session:destroy()
        elseif err then
          -- Close the current session before returning an error message
          session:close()
        end
      end
      if err then
        uncached_response(
          ngx.HTTP_INTERNAL_SERVER_ERROR,
          "application/json",
          cjson.encode({message=err, tag="no bearer, authenticate", user_role=nil}))
        goto script_end
      end
    end

    -- If authenticate hasn't rejected us above but it's "open", i.e.
    -- non-authenticated users can see the page, clear X-User and
    -- X-User-Role by setting the value to nil.
    if res ~= nil then  -- Authentication worked
      if session.data.user_id ~= nil then
        -- Load user_id and user_role from session if available
        user_id = session.data.user_id
        user_role = session.data.user_role
        -- Close the session, since we're done loading data from it
        session:close()
      else
        -- Save user_id and user_role into session for future use
        user_id = res.id_token.sub
        user_role = get_user_role(user_id)
        session.data.user_id = user_id
        session.data.user_role = user_role
        session:save()
      end

      -- Set user object for possible /api/auth/user response
      user = res.user

      -- Set Bearer header for nested requests
      --  - First tries to use session-derived access token; if it's unset,
      --    try using the response access token.
      -- TODO: Maybe only res token needed?
      local auth_token = res.access_token
      if auth_token == nil then
        auth_token, err = openidc.access_token()  -- TODO: Remove this block?
        if err ~= nil then ngx.log(ngx.ERR, err) end
      end
      if auth_token ~= nil then
        nested_auth_header = "Bearer " .. auth_token
      end
    elseif session ~= nil then
      -- Close the session, since we don't need it anymore
      session:close()
    end
  end
end

-- Either authenticated or not, so from hereon out we:
--  - Handle scripted virtual endpoints (user info, sign in, OTT stuff)
--  - Check access given the URL
--  - Set proxy-internal headers

if URI == USER_INFO_PATH then
  -- Endpoint: /api/auth/user
  --   Generates a JSON response with user data if the user is authenticated;
  --   otherwise returns a 401 Forbidden error.
  if user == nil then
    err_user_nil()
  else
    user["chord_user_role"] = user_role
    uncached_response(ngx.HTTP_OK, "application/json", cjson.encode(user))
  end
elseif URI == SIGN_IN_PATH then
  -- Endpoint: /api/auth/sign-in
  --   - If the user has not signed in, this will get caught above by the
  --     authenticate() call;
  --   - If the user just signed in and was redirected here, check the args for
  --     a redirect parameter and return a redirect if necessary.
  -- TODO: Do the same for sign-out (in certain cases)
  local args, args_error = ngx.req.get_uri_args()
  if args_error == nil then  -- If the redirect argument is set, follow through
    local redirect = args.redirect
    if type(redirect) == "string" then
      -- Skip setting the Authorization/user info headers so we don't leak
      -- anything, although I'm not sure if that would actually happen
      ngx.redirect(redirect)
      goto script_end
    end
  end
elseif URI == ONE_TIME_TOKENS_GENERATE_PATH then
  -- Endpoint: POST /api/auth/ott/generate
  --   Generates one or more one-time tokens for asynchronous authorization
  --   purposes if user is authenticated; otherwise returns a 401 Forbidden error.
  --   Called with a POST body (in JSON format) of: (for example)
  --     {"scope": "/api/some_service/", "tokens": 5}
  --   This will generate 5 one-time-use tokens that are only valid on URLs in
  --   the /api/some_service/ namespace.
  --   Scopes cannot be outside /api/ or in /api/auth

  if REQUEST_METHOD ~= "POST" then
    err_invalid_method()
    goto script_end
  end

  if user_role == nil then
    err_user_nil()
    goto script_end
  end

  ngx.req.read_body()  -- Read the request body into memory
  local req_body = cjson.decode(ngx.req.get_body_data() or "null")
  if type(req_body) ~= "table" then
    err_invalid_req_body()
    goto script_end
  end

  local scope = req_body["scope"]
  if not scope or type(scope) ~= "string" then
    uncached_response(ngx.HTTP_BAD_REQUEST, "application/json",
      cjson.encode({message="Missing or invalid token scope", tag="invalid scope", user_role=user_role}))
    goto script_end
  end

  -- Validate that the scope asked for is reasonable
  --   - Must be in a /api/[a-zA-Z0-9]+/ namespace
  --   - Cannot be specific to the auth namespace

  if not scope:match("^/api/%a[%w-_]*/") or scope:match("^/api/auth") then
    uncached_response(ngx.HTTP_BAD_REQUEST, "application/json",
      cjson.encode({message="Bad token scope", tag="bad scope", user_role=user_role}))
    goto script_end
  end

  local n_tokens = math.max(req_body["number"] or 1, 1)

  -- Don't let a user request more than 30 OTTs at a time
  if n_tokens > 30 then
    uncached_response(ngx.HTTP_BAD_REQUEST, "application/json",
      cjson.encode({message="Too many OTTs requested", tag="too many tokens", user_role=user_role}))
    goto script_end
  end

  red_ok, red_err = red:connect(REDIS_SOCKET)
  if red_err then
    err_redis("redis conn")
    goto script_end
  end

  -- Update NGINX internal time cache
  ngx.update_time()

  local new_token
  local new_tokens = {}

  -- Generate n_tokens new tokens
  red:init_pipeline(5 * n_tokens)
  for _ = 1, n_tokens do
    -- Generate a new token (using OpenSSL via lua-resty-random), 128 characters long
    -- Does not use the token method, since that does not use OpenSSL
    new_token = str.to_hex(random.bytes(64))
    -- TODO: RANDOM CAN RETURN NIL, HANDLE THIS
    table.insert(new_tokens, new_token)
    red:hset("bento_ott:expiry", new_token, ngx.time() + 604800)  -- Set expiry to current time + 7 days
    red:hset("bento_ott:scope", new_token, scope)
    red:hset("bento_ott:user", new_token, cjson.encode(user))
    red:hset("bento_ott:user_id", new_token, user_id)
    red:hset("bento_ott:user_role", new_token, user_role)
  end
  red:commit_pipeline()

  -- Put Redis connection into a keepalive pool for 30 seconds
  red_ok, red_err = red:set_keepalive(30000, 100)
  if red_err then
    err_redis("redis keepalive failed")
    -- TODO: Do we need to invalidate the tokens here? They aren't really guessable anyway
    goto script_end
  end

  -- Return the newly-generated tokens to the requester
  uncached_response(ngx.HTTP_OK, "application/json", cjson.encode(new_tokens))
elseif URI == ONE_TIME_TOKENS_INVALIDATE_PATH then
  -- Endpoint: DELETE /api/auth/ott/invalidate
  --   Invalidates a token passed in the request body (format: {"token": "..."}) if the
  --   supplied token exists. This endpoint is idempotent, and will return 204 (assuming
  --   nothing went wrong on the server) even if the token did not exist. Regardless, the
  --   end state is that the supplied token is guaranteed not to be valid anymore.

  if REQUEST_METHOD ~= "DELETE" then
    err_invalid_method()
    goto script_end
  end

  if user_role ~= "owner" then
    err_user_not_owner()
    goto script_end
  end

  ngx.req.read_body()  -- Read the request body into memory
  local req_body = cjson.decode(ngx.req.get_body_data() or "null")
  if type(req_body) ~= "table" then
    err_invalid_req_body()
    goto script_end
  end

  local token = req_body["token"]
  if not token or type(token) ~= "string" then
    uncached_response(ngx.HTTP_BAD_REQUEST, "application/json",
      cjson.encode({message="Missing or invalid token", tag="invalid token", user_role=user_role}))
    goto script_end
  end

  red_ok, red_err = red:connect(REDIS_SOCKET)
  if red_err then
    err_redis("redis conn")
    goto script_end
  end

  invalidate_ott(red, token)

  -- Put Redis connection into a keepalive pool for 30 seconds
  red_ok, red_err = red:set_keepalive(30000, 100)
  if red_err then
    err_redis("redis keepalive failed")
    goto script_end
  end

  -- We're good to respond in the affirmative
  uncached_response(ngx.HTTP_NO_CONTENT)
elseif URI == ONE_TIME_TOKENS_INVALIDATE_ALL_PATH then
  -- Endpoint: DELETE /api/auth/ott/invalidate_all
  --   Invalidates all one-time use tokens in the Redis store. This endpoint is
  --   idempotent, and will return 204 (assuming nothing went wrong on the server) even if
  --   no tokens currently exist. Regardless, the end state is that all OTTs are
  --   guaranteed not to be valid anymore.

  if REQUEST_METHOD ~= "DELETE" then
    err_invalid_method()
    goto script_end
  end

  if user_role ~= "owner" then
    err_user_not_owner()
    goto script_end
  end

  red_ok, red_err = red:connect(REDIS_SOCKET)
  if red_err then
    err_redis("redis conn")
    goto script_end
  end

  red:init_pipeline(5)
  red:del("bento_ott:expiry")
  red:del("bento_ott:scope")
  red:del("bento_ott:user")
  red:del("bento_ott:user_id")
  red:del("bento_ott:user_role")
  red:commit_pipeline()

  -- Put Redis connection into a keepalive pool for 30 seconds
  red_ok, red_err = red:set_keepalive(30000, 100)
  if red_err then
    err_redis("redis keepalive failed")
    goto script_end
  end

  -- We're good to respond in the affirmative
  uncached_response(ngx.HTTP_NO_CONTENT)
elseif is_private_uri and user_role ~= "owner" then
  -- Check owner status before allowing through the proxy
  -- TODO: Check ownership / grants?
  err_user_not_owner()
end

-- Clear and possibly set internal headers to inform services of user identity
-- and their basic role/permissions set (either the node's owner or a user of
-- another type.)
-- Set an X-Authorization header containing a valid Bearer token for nested
-- requests to other services.
-- TODO: Pull this from session for performance
ngx.req.set_header("X-User", user_id)
ngx.req.set_header("X-User-Role", user_role)
ngx.req.set_header("X-Authorization", nested_auth_header)

-- If an unrecoverable error occurred, it will jump here to skip everything and
-- avoid trying to execute code while in an invalid state.
::script_end::