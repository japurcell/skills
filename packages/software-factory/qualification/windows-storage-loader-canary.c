/* Qualification-only ABI canary. Pre-load authority belongs to the external
 * trusted provisioner, never to this module. No storage or owned OS resources. */
#ifndef NAPI_VERSION
#define NAPI_VERSION 8
#endif
#if NAPI_VERSION != 8
#error Positive canary requires Node-API 8
#endif
/* A separately receipted trusted negative build exercises actual ABI refusal. */
#if defined(FACTORY_LOADER_NEGATIVE_API)
#undef NAPI_VERSION
#define NAPI_VERSION 999
#endif
#include <node_api.h>

static napi_value probe(napi_env env, napi_callback_info info) {
  napi_value result;
  (void)info;
  if (napi_create_string_utf8(env, "windows-storage-loader-canary-v1",
                            NAPI_AUTO_LENGTH, &result) != napi_ok) {
    (void)napi_throw_error(env, "CANARY", "canary call failed");
    return NULL;
  }
  return result;
}

NAPI_MODULE_INIT() {
  napi_value function;
  if (napi_create_function(env, "probe", NAPI_AUTO_LENGTH, probe, NULL,
                           &function) != napi_ok ||
      napi_set_named_property(env, exports, "probe", function) != napi_ok) {
    (void)napi_throw_error(env, "CANARY", "canary initialization failed");
    return NULL;
  }
  return exports;
}
