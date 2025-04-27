from . import Log

log = Log()
log._logger().info("main @ Log")
log.testfunc()


print(log.get_sibling_from_basetype(Log.Impl))

