import commands, os, traceback, pexpect, time, subprocess
from utils.Python.utils import Utils as utils
from repos.entitlement.ent_utils import ent_utils as eu
from repos.entitlement.ent_env import ent_env as ee

def tc_Clean_Virtwho(params):
	""" Clean up virt-who test environment """
	try:
		try:
			logger = params['logger']
			eu().RESET_RESULT()
			logger.info("=============== Begin of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])

			if "vcentermachine_ip" in params.keys():
				vcentermachine_ip = params['vcentermachine_ip']
				VIRTWHO_ESX_OWNER = "ACME_Corporation"
				VIRTWHO_ESX_ENV = "env1"
				VIRTWHO_ESX_SERVER = vcentermachine_ip
				VIRTWHO_ESX_USERNAME = params.get("vcentermachine_username")
				VIRTWHO_ESX_PASSWORD = params.get("vcentermachine_password")
				ESX_HOST_1 = ee.esx_host_ip
				vmware_cmd_ip = ee.vmware_cmd_ip
				eu().SET_RESULT(0)

			if "targetmachine_ip" in params.keys():
				# (1)undefine all guests
				eu().vw_undefine_all_guests(logger, params)
				# (2)stop virt-who service - restart firstly to get current all guest status inputted into the rhsm.log.
				# #restart virt-who service
				eu().vw_restart_virtwho(logger)
				# #stop virt-who service
				eu().vw_stop_virtwho(logger)
				# (3)unregister the host
				if eu().sub_isregistered(logger):
					eu().sub_unregister(logger)
				# (4)unmount image path in source machine
				eu().unmount_imagepath_in_sourcemachine(logger, ee.imagepath)
				# (5)clean env for migration if needed
				if params.has_key("targetmachine_ip"):
					logger.info("-------- Begin to clean env for migration --------")
					targetmachine_ip = params["targetmachine_ip"]
					# 1)unmount image path in target machine
					eu().unmount_imagepath_in_targetmachine(logger, ee.imagepath, targetmachine_ip)
					# 2)unmount the rhsm log of the target machine
					eu().unmount_rhsmlog_of_targetmachine(logger, ee.rhsmlog_for_targetmachine)
					# 3)stop virt-who service - restart firstly to get current all guest status inputted into the rhsm.log.
					# #restart virt-who service
					eu().vw_restart_virtwho(logger, targetmachine_ip)
					# #stop virt-who service
					eu().vw_stop_virtwho(logger, targetmachine_ip)
					# 4)unregister the target machine
					if eu().sub_isregistered(logger, targetmachine_ip):
						eu().sub_unregister(logger, targetmachine_ip)
					logger.info("-------- End to clean env for migration --------")
				eu().SET_RESULT(0)
		except Exception, e:
			logger.error("Test Failed due to error happened: " + str(e))
			logger.error(traceback.format_exc())
			eu().SET_RESULT(1)
	finally:
		logger.info("=============== End of Running Test Case: %s ===============" % __name__[str.rindex(__name__, ".") + 1:])
		return eu().TEST_RESULT()
