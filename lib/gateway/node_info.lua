-- Script to return public node config metadata via the config file contents.

local cjson = require("cjson")

local response = {
  CHORD_URL=os.getenv("CHORD_URL"),
  OIDC_DISCOVERY_URI=os.getenv("OIDC_DISCOVERY_URI"),
}

ngx.status = 200
ngx.header["Content-Type"] = "application/json"
ngx.say(cjson.encode(response))
