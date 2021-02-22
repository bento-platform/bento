-- Script to return public node config metadata via the config file contents.

local cjson = require("cjson")

local auth_file = assert(io.open("/usr/local/openresty/nginx/auth_config.json"))
local auth_params = cjson.decode(auth_file:read("*all"))
auth_file:close()

local config_file = assert(io.open("/usr/local/openresty/nginx/instance_config.json"))
local config_params = cjson.decode(config_file:read("*all"))
config_file:close()

local response = {
  CHORD_URL=config_params["CHORD_URL"],
  OIDC_DISCOVERY_URI=auth_params["OIDC_DISCOVERY_URI"],
}

ngx.status = 200
ngx.header["Content-Type"] = "application/json"
ngx.say(cjson.encode(response))
