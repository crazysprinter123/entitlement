import sys, os, subprocess, commands, string, re, random, time, pexpect
from utils.Python.utils import Utils as utils
from repos.domain import define
from repos.domain import undefine
from repos.domain import suspend
from repos.domain import resume
from repos.domain import shutdown
from repos.domain import start
from repos.domain import destroy
from repos.domain import migrate
from repos.entitlement.ent_env import ent_env as ee

class ent_utils:

	# ========================================================
	# 	   0. 'Basic' Common Functions
	# ========================================================

	def runcmd(self, logger, cmd, cmddesc="", targetmachine_ip="", showlogger=True):
		if targetmachine_ip == "":
			(ret, output) = commands.getstatusoutput(cmd)
		else:
			if "redhat.com" in targetmachine_ip:
				# run in beaker
				(ret, output) = utils().remote_exec_pexpect(targetmachine_ip, "root", "red2015", cmd)
			else:
				(ret, output) = utils().remote_exec_pexpect(targetmachine_ip, "root", "redhat", cmd)
		if cmddesc != "":
			cmddesc = " of " + cmddesc
		if showlogger:
			logger.info(" [command]%s: %s" % (cmddesc, cmd))
			logger.info(" [result ]%s: %s" % (cmddesc, str(ret)))
			logger.info(" [output ]%s: %s \n" % (cmddesc, output))
		return ret, output

	def runcmd_byuser(self, logger, cmd, cmddesc="", targetmachine_ip="", username="root", password="qwe123P", showlogger=True):
		if targetmachine_ip == "":
			(ret, output) = commands.getstatusoutput(cmd)
		else:
			(ret, output) = self.remote_esx_pexpect(targetmachine_ip, username, password, cmd)
		if cmddesc != "":
			cmddesc = " of " + cmddesc
		if showlogger:
			logger.info(" [command]%s: %s" % (cmddesc, cmd))
			logger.info(" [result ]%s: %s" % (cmddesc, str(ret)))
			logger.info(" [output ]%s: %s \n" % (cmddesc, output))
		return ret, output

	def runcmd_rhevm(self, logger, cmd, cmddesc="run rhevm-shell command", rhevm_ip="", showlogger=True):
		# 1. add rhevm_script file
		utils().remote_exec_pexpect(rhevm_ip, "root", "redhat", "echo '%s' > /tmp/rhevm_script" % cmd)
		# 2. change rhevm_control file
		utils().remote_exec_pexpect(rhevm_ip, "root", "redhat", "echo 1 > /tmp/rhevm_control")
		if self.check_rhevm_shell_finished(logger, rhevm_ip):
			# 3. get rhevm_result file
			(ret, output) = utils().remote_exec_pexpect(rhevm_ip, "root", "redhat", "cat /tmp/rhevm_result")
		if cmddesc != "":
			cmddesc = " of " + cmddesc
		if showlogger:
			logger.info(" [command]%s: %s" % (cmddesc, cmd))
			logger.info(" [result ]%s: %s" % (cmddesc, str(ret)))
			logger.info(" [output ]%s: %s \n" % (cmddesc, output))
		return ret, output

	def runcmd_indns(self, logger, cmd, cmddesc="", targetmachine_ip="", username="root", password="forsamdns", showlogger=True):
		if targetmachine_ip == "":
			(ret, output) = commands.getstatusoutput(cmd)
		else:
			(ret, output) = utils().remote_exec_pexpect(targetmachine_ip, username, password, cmd)
		if cmddesc != "":
			cmddesc = " of " + cmddesc
		if showlogger:
			logger.info(" [command]%s: %s" % (cmddesc, cmd))
			logger.info(" [result ]%s: %s" % (cmddesc, str(ret)))
			logger.info(" [output ]%s: %s \n" % (cmddesc, output))
		return ret, output

	def remote_esx_pexpect(self, hostname, username, password, cmd):
		""" Remote exec function via pexpect """
		user_hostname = "%s@%s" % (username, hostname)
		child = pexpect.spawn("/usr/bin/ssh", [user_hostname, cmd], timeout=1800, maxread=2000, logfile=None)
		while True:
			index = child.expect(['(yes\/no)', 'Password:', pexpect.EOF, pexpect.TIMEOUT])
			if index == 0:
				child.sendline("yes")
			elif index == 1:
				child.sendline(password)
			elif index == 2:
				child.close()
				return child.exitstatus, child.before
			elif index == 3:
				child.close()
				return 1, ""
		return 0

	def runcmd_subprocess(self, logger, cmd, cmddesc=""):
		logger.info("[ command of subprocess]%s: %s" % (cmddesc, cmd))
		ret = subprocess.call(cmd, shell=True)
		# result.stdout.readlines())
		# handle = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		# ##logger.info("[ result of subprocess] : %s" % handle.communicate()[0]
		return ret, ""

	def runcmd_rhevmprocess(self, logger, cmd, cmddesc=""):
		logger.info("[ command of rhevm-shell]%s: %s" % (cmddesc, cmd))
		output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		for line in output.stdout.readlines():
			return line

	def get_HG_info(self, targetmachine_ip):
		if targetmachine_ip == "":
			host_guest_info = "in host machine"
		else:
			host_guest_info = "in guest machine %s" % targetmachine_ip
		return host_guest_info

	def get_guest_IP(self, logger, guest_name):
		mac = utils().get_dom_mac_addr(guest_name)
		guestip = utils().mac_to_ip(mac)
		if guestip == None:
			logger.error("Failed to get guest IP.")
			self.SET_RESULT(1)
		else:
			logger.info("Succeeded to get guest IP: %s" % guestip)
			return guestip

	# For return test result
	RESULT = 1
	def RESET_RESULT(self):
		global RESULT
		RESULT = 1
		# print "RESULT has been reseted %s" % RESULT
	def TEST_RESULT(self):
		global RESULT
		if RESULT > 1:
			RESULT = 1
		# print "RESULT has been returned %s" % RESULT
		return RESULT
	def SET_RESULT(self, step_result):
		global RESULT
		if step_result == 0:
			# print "RESULT has been minused"
			RESULT = RESULT - 1
			# print "RESULT = %s" % RESULT
		else:
			# print "RESULT has been added"
			RESULT = RESULT + step_result
			# print "RESULT = %s" % RESULT

	# ========================================================
	# 	1. 'RHSM' Test Common Functions
	# ========================================================

	def sub_register(self, logger, username, password, targetmachine_ip=""):
		''' Register the machine. '''
		# cmd = "subscription-manager clean"
		# ret, output = self.runcmd(logger, cmd, "subscription-manager clean", targetmachine_ip)
		cmd = "subscription-manager register --username=%s --password=%s" % (username, password)
		ret, output = self.runcmd(logger, cmd, "register system", targetmachine_ip)
		if ret == 0 or "The system has been registered with id:" in output or "This system is already registered" in output:
			logger.info("Succeeded to register system %s" % self.get_HG_info(targetmachine_ip))
		else:
			logger.error("Failed to register system %s" % self.get_HG_info(targetmachine_ip))
			self.SET_RESULT(1)

	def sub_isregistered(self, logger, targetmachine_ip=""):
		''' Check whether the machine is registered. '''
		cmd = "subscription-manager identity"
		ret, output = self.runcmd(logger, cmd, "check whether the machine is registered", targetmachine_ip)
		if ret == 0:
			logger.info("System %s is registered." % self.get_HG_info(targetmachine_ip))
			return True
		else: 
			logger.info("System %s is not registered." % self.get_HG_info(targetmachine_ip))
			return False

	def sub_unregister(self, logger, targetmachine_ip=""):
		''' Unregister the machine. '''
		if self.sub_isregistered(logger, targetmachine_ip):
			# need to sleep before destroy guest or else register error happens 
			cmd = "subscription-manager unregister; sleep 20"
			ret, output = self.runcmd(logger, cmd, "unregister system", targetmachine_ip)

			# In order to avoid bug995292 in the RHEL5.11
			#if ret == 0 and ("System has been un-registered" in output or "System has been unregistered" in output):
			if ret == 0 :
				logger.info("Succeeded to unregister %s." % self.get_HG_info(targetmachine_ip))
			else:
				logger.error("Failed to unregister %s." % self.get_HG_info(targetmachine_ip))
				self.SET_RESULT(1)
		else:
			logger.info("The machine is not registered to server now, no need to do unregister.")

	def sub_listavailpools(self, logger, productid, targetmachine_ip="", showlog=True):
		''' List available pools.'''
		cmd = "subscription-manager list --available"
		ret, output = self.runcmd(logger, cmd, "run 'subscription-manager list --available'", targetmachine_ip, showlogger=showlog)
		if ret == 0:
			if "No Available subscription pools to list" not in output:
				if productid in output:
					logger.info("Succeeded to run 'subscription-manager list --available' %s." % self.get_HG_info(targetmachine_ip))
					pool_list = self.__parse_avail_pools(logger, output)
					return pool_list
				else:
					logger.error("Failed to run 'subscription-manager list --available' %s - Not the right available pools are listed!" % self.get_HG_info(targetmachine_ip))
					self.SET_RESULT(1)
			else:
				logger.error("Failed to run 'subscription-manager list --available' %s - There is no Available subscription pools to list!" % self.get_HG_info(targetmachine_ip))
				self.SET_RESULT(1)
		else:
			logger.error("Failed to run 'subscription-manager list --available' %s." % self.get_HG_info(targetmachine_ip))
			self.SET_RESULT(1)

	def sub_datacenter_listavailpools(self, logger, subscription_name, targetmachine_ip="", showlog=True):
		''' List available pools.'''
		cmd = "subscription-manager list --available"
		ret, output = self.runcmd(logger, cmd, "list available subscriptions", targetmachine_ip, showlogger=showlog)
		if ret == 0:
			if "No Available subscription pools to list" not in output:
				if subscription_name in output:
					logger.info("Succeeded to list the right available pools %s." % self.get_HG_info(targetmachine_ip))
					pool_list = self.__parse_avail_pools(logger, output)
					return pool_list
				else:
					logger.error("Failed to list available pools %s - Not the right available pools are listed!" % self.get_HG_info(targetmachine_ip))
					self.SET_RESULT(1)
			else:
				logger.error("Failed to list available pools %s - There is no Available subscription pools to list!" % self.get_HG_info(targetmachine_ip))
				self.SET_RESULT(1)
		else:
			logger.error("Failed to list available pools %s." % self.get_HG_info(targetmachine_ip))
			self.SET_RESULT(1)

	def __parse_avail_pools(self, logger, output):
		datalines = output.splitlines()
		pool_list = []
		data_segs = []
		segs = []
		for line in datalines:
			if ("Product Name:" in line) or ("ProductName:" in line) or ("Subscription Name:" in line):
				segs.append(line)
			elif segs:
				# change this section for more than 1 lines without ":" exist
				if ":" in line:
					segs.append(line)
				else:
					segs[-1] = segs[-1] + " " + line.strip()
			if ("Machine Type:" in line) or ("MachineType:" in line) or ("System Type:" in line):
				data_segs.append(segs)
				segs = []

# 		#This fuction failed when more than 1 lines without ":" exist
# 		# handle item with multi rows
# 		for seg in data_segs:
# 			length = len(seg)
# 			for index in range(0, length):
# 				if ":" not in seg[index]:
# 					seg[index - 1] = seg[index - 1] + " " + seg[index].strip()
# 			for item in seg:
# 				if ":" not in item:
# 					seg.remove(item)

		# parse detail information for each pool
		for seg in data_segs:
			pool_dict = {}
			for item in seg:
				keyitem = item.split(":")[0].replace(" ", "")
				valueitem = item.split(":")[1].strip()
				pool_dict[keyitem] = valueitem
			pool_list.append(pool_dict)
		return pool_list

	def sub_subscribetopool(self, logger, poolid, targetmachine_ip=""):
		''' Subscribe to a pool. '''
		cmd = "subscription-manager subscribe --pool=%s" % (poolid)
		ret, output = self.runcmd(logger, cmd, "subscribe by --pool", targetmachine_ip)
		if ret == 0:
			if "Successfully " in output:
				logger.info("Succeeded to subscribe to a pool %s." % self.get_HG_info(targetmachine_ip))
			else:
				logger.error("Failed to show correct information after subscribing %s." % self.get_HG_info(targetmachine_ip))
				self.SET_RESULT(1)
		else:
			logger.error("Failed to subscribe to a pool %s." % self.get_HG_info(targetmachine_ip))
			self.SET_RESULT(1)

	def sub_subscribe_instance_pool(self, logger, poolid, targetmachine_ip=""):
		''' Subscribe to an instance pool. '''
		cmd = "subscription-manager subscribe --pool=%s --quantity=2" % (poolid)
		ret, output = self.runcmd(logger, cmd, "subscribe an instance pool", targetmachine_ip)
		if ret == 0:
			if "Successfully " in output:
				logger.info("Succeeded to subscribe an instance pool %s." % self.get_HG_info(targetmachine_ip))
			else:
				logger.error("Failed to subscribe an instance pool %s." % self.get_HG_info(targetmachine_ip))
				self.SET_RESULT(1)
		else:
			logger.error("Failed to subscribe an instance pool %s." % self.get_HG_info(targetmachine_ip))
			self.SET_RESULT(1)

	def sub_subscribetopool_of_product(self, logger, productid, targetmachine_ip=""):
		''' Subscribe to the pool of the product: productid. '''
		availpoollist = self.sub_listavailpools(logger, productid, targetmachine_ip)
		if availpoollist != None:
			rindex = -1
			for index in range(0, len(availpoollist)):
				if("SKU" in availpoollist[index] and availpoollist[index]["SKU"] == productid):
					rindex = index
					break
				elif("ProductId" in availpoollist[index] and availpoollist[index]["ProductId"] == productid):
					rindex = index
					break
			if rindex == -1:
				logger.error("Failed to show find the bonus pool")
				self.SET_RESULT(1)
			if "PoolID" in availpoollist[index]:
				poolid = availpoollist[rindex]["PoolID"]
			else:
				poolid = availpoollist[rindex]["PoolId"]
			self.sub_subscribetopool(logger, poolid, targetmachine_ip)
		else:
			logger.error("Failed to subscribe to the pool of the product: %s - due to failed to list available pools." % productid)
			self.SET_RESULT(1)

	def sub_subscribe_to_bonus_pool(self, logger, productid, guest_ip=""):
		''' Subscribe the registered guest to the corresponding bonus pool of the product: productid. '''
		availpoollistguest = self.sub_listavailpools(logger, productid, guest_ip)
		if availpoollistguest != None:
			rindex = -1
			for index in range(0, len(availpoollistguest)):
				# if("SKU" in availpoollistguest[index] and availpoollistguest[index]["SKU"] == productid and availpoollistguest[index][self.get_type_name(availpoollistguest[index])] == "virtual"):
				if("SKU" in availpoollistguest[index] and availpoollistguest[index]["SKU"] == productid and self.check_type_virtual(availpoollistguest[index])):
					rindex = index
					break
				# elif("ProductId" in availpoollistguest[index] and availpoollistguest[index]["ProductId"] == productid and availpoollistguest[index][self.get_type_name(availpoollistguest[index])] == "virtual"):
				elif("ProductId" in availpoollistguest[index] and availpoollistguest[index]["ProductId"] == productid and self.check_type_virtual(availpoollistguest[index])):
					rindex = index
					break
			if rindex == -1:
				logger.error("Failed to show find the bonus pool")
				self.SET_RESULT(1)
			if "PoolID" in availpoollistguest[index]:
				gpoolid = availpoollistguest[rindex]["PoolID"]
			else:
				gpoolid = availpoollistguest[rindex]["PoolId"]
			self.sub_subscribetopool(logger, gpoolid, guest_ip)
		else:
			logger.error("Failed to subscribe the guest to the bonus pool of the product: %s - due to failed to list available pools." % productid)
			self.SET_RESULT(1)

	def subscribe_datacenter_bonus_pool(self, logger, subscription_name, guest_ip=""):
		''' Subscribe the registered guest to the corresponding bonus pool of the product: productid. '''
		availpoollistguest = self.sub_datacenter_listavailpools(logger, subscription_name, guest_ip)
		if availpoollistguest != None:
			for index in range(0, len(availpoollistguest)):
				if("SubscriptionName" in availpoollistguest[index] and availpoollistguest[index]["SubscriptionName"] == subscription_name and self.check_type_virtual(availpoollistguest[index])):
					rindex = index
					break
			if "PoolID" in availpoollistguest[rindex]:
				gpoolid = availpoollistguest[rindex]["PoolID"]
			else:
				gpoolid = availpoollistguest[rindex]["PoolId"]
			self.sub_subscribetopool(logger, gpoolid, guest_ip)
		else:
			logger.error("Failed to subscribe the guest to the bonus pool of the product: %s - due to failed to list available pools." % subscription_name)
			self.SET_RESULT(1)

	def subscribe_instance_pool(self, logger, SKU_id, guest_ip=""):
		''' subscribe_instance_pool '''
		availpoollistguest = self.sub_listavailpools(logger, SKU_id, guest_ip)
		if availpoollistguest != None:
			for index in range(0, len(availpoollistguest)):
				if("SKU" in availpoollistguest[index] and availpoollistguest[index]["SKU"] == SKU_id):
					rindex = index
					break
			if "PoolID" in availpoollistguest[index]:
				gpoolid = availpoollistguest[rindex]["PoolID"]
			else:
				gpoolid = availpoollistguest[rindex]["PoolId"]
			self.sub_subscribe_instance_pool(logger, gpoolid, guest_ip)
		else:
			logger.error("Failed to subscribe the guest to the bonus pool of the product: %s - due to failed to list available pools." % SKU_id)
			self.SET_RESULT(1)

	def get_pool_by_SKU(self, logger, SKU_id, guest_ip=""):
		''' get_pool_by_SKU '''
		availpoollistguest = self.sub_listavailpools(logger, SKU_id, guest_ip)
		if availpoollistguest != None:
			for index in range(0, len(availpoollistguest)):
				if("SKU" in availpoollistguest[index] and availpoollistguest[index]["SKU"] == SKU_id):
					rindex = index
					break
			if "PoolID" in availpoollistguest[index]:
				gpoolid = availpoollistguest[rindex]["PoolID"]
			else:
				gpoolid = availpoollistguest[rindex]["PoolId"]
			return gpoolid
		else:
			logger.error("Failed to subscribe the guest to the bonus pool of the product: %s - due to failed to list available pools." % SKU_id)
			self.SET_RESULT(1)

	def get_SKU_attribute(self, logger, SKU_id, attribute_key, guest_ip=""):
		availpoollistguest = self.sub_listavailpools(logger, SKU_id, guest_ip)
		if availpoollistguest != None:
			for index in range(0, len(availpoollistguest)):
				if("SKU" in availpoollistguest[index] and availpoollistguest[index]["SKU"] == SKU_id):
					rindex = index
					break
			if attribute_key in availpoollistguest[index]:
				attribute_value = availpoollistguest[rindex][attribute_key]
			return attribute_value
		else:
			logger.error("Failed to list available subscriptions" % SKU_id)
			self.SET_RESULT(1)

	def sub_autosubscribe(self, logger, autosubprod, targetmachine_ip=""):
		cmd = "subscription-manager subscribe --auto"
		(ret, output) = self.runcmd(logger, cmd, "auto-subscribe", targetmachine_ip="")
		if ret == 0:
			if (autosubprod in output) and ("Subscribed" in output) and ("Not Subscribed" not in output):
				logger.info("It's successful to auto-subscribe.")
			else:
				logger.error("Test Failed - Failed to auto-subscribe correct product.")
		else:
			logger.error("Test Failed - Failed to auto-subscribe.")

	def auto_subscribe(self, logger, targetmachine_ip=""):
		cmd = "subscription-manager subscribe --auto"
		(ret, output) = self.runcmd(logger, cmd, "auto-subscribe", targetmachine_ip="")
		if ret == 0:
			if ("Subscribed" in output) and ("Not Subscribed" not in output):
				logger.info("It's successful to auto-subscribe.")
			else:
				logger.error("Test Failed - Failed to auto-subscribe correct product.")
		else:
			logger.error("Test Failed - Failed to auto-subscribe.")

	def get_type_name(self, pool_dict):
		if "MachineType" in pool_dict.keys():
			TypeName = "MachineType"
		elif "SystemType" in pool_dict.keys():
			TypeName = "SystemType"
		# print "TypeName = %s" % TypeName
		return TypeName
	
	def check_type_virtual(self, pool_dict):
		if "MachineType" in pool_dict.keys():
			TypeName = "MachineType"
		elif "SystemType" in pool_dict.keys():
			TypeName = "SystemType"
		# print "TypeName = %s" % TypeName
		# print pool_dict[TypeName] == "Virtual"
		return pool_dict[TypeName] == "Virtual" or pool_dict[TypeName] == "virtual"

	def sub_unsubscribe(self, logger, targetmachine_ip=""):
		''' Unsubscribe from all entitlements. '''
		cmd = "subscription-manager unsubscribe --all"
		ret, output = self.runcmd(logger, cmd, "unsubscribe all", targetmachine_ip)

		if ret == 0:
			cmd = "ls /etc/pki/entitlement/ | grep -v key.pem"
			ret1, output1 = self.runcmd(logger, cmd, "check whether key.pem exist", targetmachine_ip)

			if ret1 == 0 :
				logger.error("Failed to unsubscribe all entitlements %s." % self.get_HG_info(targetmachine_ip))
				self.SET_RESULT(1)
			else:
				logger.info("Succeeded to unsubscribe all entitlements %s." % self.get_HG_info(targetmachine_ip))
		else:
			logger.error("Failed to unsubscribe %s." % self.get_HG_info(targetmachine_ip))

	def sub_listconsumed(self, logger, productname, targetmachine_ip="", productexists=True):
		''' List consumed entitlements. '''
		cmd = "subscription-manager list --consumed"
		ret, output = self.runcmd(logger, cmd, "list consumed subscriptions", targetmachine_ip)
		if ret == 0:
			if productexists:
				if "No Consumed subscription pools to list" not in output:
					if productname in output:
						logger.info("Succeeded to list the right consumed subscription %s." % self.get_HG_info(targetmachine_ip))
					else:
						logger.error("Failed to list consumed subscription %s - Not the right consumed subscription is listed!" % self.get_HG_info(targetmachine_ip))
						self.SET_RESULT(1)
				else:
					logger.error("Failed to list consumed subscription %s - There is no consumed subscription to list!")
					self.SET_RESULT(1)
			else:
				if productname not in output:
					logger.info("Succeeded to check entitlements %s - the product '%s' is not subscribed now." % (self.get_HG_info(targetmachine_ip), productname))
				else:
					logger.error("Failed to check entitlements %s - the product '%s' is still subscribed now." % (self.get_HG_info(targetmachine_ip), productname))
					self.SET_RESULT(1)
		else:
			logger.error("Failed to list consumed subscriptions.")
			self.SET_RESULT(1)

	def sub_refresh(self, logger, targetmachine_ip=""):
		''' Refresh all local data. '''
		cmd = "subscription-manager refresh; sleep 10"
		ret, output = self.runcmd(logger, cmd, "subscription fresh", targetmachine_ip)
		if ret == 0 and "All local data refreshed" in output:
			logger.info("Succeeded to refresh all local data %s." % self.get_HG_info(targetmachine_ip))
		else:
			logger.error("Failed to refresh all local data %s." % self.get_HG_info(targetmachine_ip))
			self.SET_RESULT(1)

	# ========================================================
	# 	2. 'Virt-Who' Test Common Functions
	# ========================================================

	def get_env(self, logger):
		env = {}
		cmd = "grep '^hostname = subscription.rhn.stage.redhat.com' /etc/rhsm/rhsm.conf"
		ret, output = self.runcmd(logger, cmd, "check stage config")
		if "hostname = subscription.rhn.stage.redhat.com" == output:
			# logger.info("**** Auto Suite Running Against Stage Candlepin ****")
			Stage = True
		else:
			# logger.info("**** Auto Suite Running Against SAM ****")
			Stage = False
		cmd = "echo $(python -c \"import yum, pprint; yb = yum.YumBase(); pprint.pprint(yb.conf.yumvar, width=1)\" | grep 'releasever' | awk -F\":\" '{print $2}' | sed  -e \"s/^ '//\" -e \"s/'}$//\" -e \"s/',$//\")"
		ret, output = self.runcmd(logger, cmd, "get_env")
		if Stage :
			env["username"] = ee.username_stage
			env["password"] = ee.password_stage
		else:
			if "5Client" in output:
				env["username"] = ee.username1s
				env["password"] = ee.password1s
				env["autosubprod"] = ee.autosubprod1s
				env["installedproductname"] = ee.installedproductname1s
				env["productid"] = ee.productid1s
				env["pid"] = ee.pid1s
				env["pkgtoinstall"] = ee.pkgtoinstall1s
				env["productrepo"] = ee.productrepo1s
				env["betarepo"] = ee.betarepo1s
			elif "5Server" in output:
				env["username"] = ee.username2s
				env["password"] = ee.password2s
				env["autosubprod"] = ee.autosubprod2s
				env["installedproductname"] = ee.installedproductname2s
				env["productid"] = ee.productid2s
				env["pid"] = ee.pid2s
				env["pkgtoinstall"] = ee.pkgtoinstall2s
				env["productrepo"] = ee.productrepo2s
				env["betarepo"] = ee.betarepo2s
			elif "5Workstation" in output:
				env["username"] = ee.username3s
				env["password"] = ee.password3s
			elif ("6Server" in output) or ("6Client" in output):
				env["username"] = ee.username4s
				env["password"] = ee.password4s
				env["autosubprod"] = ee.autosubprod4s
			elif "6Workstation" in output:
				env["username"] = ee.username5s
				env["password"] = ee.password5s
			elif ("7Server" in output) or ("7Client" in output):
				env["username"] = ee.username4s
				env["password"] = ee.password4s
				env["autosubprod"] = ee.autosubprod4s
			elif "7Workstation" in output:
				env["username"] = ee.username5s
				env["password"] = ee.password5s
			elif "6ComputeNode" in output:
				env["username"] = ee.username5s
				env["password"] = ee.password5s	
		return env

	def above_7_serials(self, logger):
		cmd = "echo $(python -c \"import yum, pprint; yb = yum.YumBase(); pprint.pprint(yb.conf.yumvar, width=1)\" | grep 'releasever' | awk -F\":\" '{print $2}' | sed  -e \"s/^ '//\" -e \"s/'}$//\" -e \"s/',$//\")"
		ret, output = self.runcmd(logger, cmd, "get rhel version")
		if output[0:1] >= 7:
			logger.info("System version is above or equal 7 serials")
			return True
		else:
			logger.info("System version is bellow 7 serials")
			return False

	def configure_host(self, logger, samhostname, samhostip, targetmachine_ip=""):
		''' configure the host machine. '''
		if samhostname != None and samhostip != None:
			# add sam hostip and hostname in /etc/hosts
			cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (samhostname, samhostip, samhostname)
			ret, output = self.runcmd(logger, cmd, "configure /etc/hosts", targetmachine_ip)
			if ret == 0:
				logger.info("Succeeded to add sam hostip %s and hostname %s %s." % (samhostip, samhostname, self.get_HG_info(targetmachine_ip)))
			else:
				logger.error("Failed to add sam hostip %s and hostname %s %s." % (samhostip, samhostname, self.get_HG_info(targetmachine_ip)))
				self.SET_RESULT(1)
			# config hostname, prefix, port, baseurl and repo_ca_crt by installing candlepin-cert
			cmd = "rpm -qa | grep candlepin-cert-consumer"
			ret, output = self.runcmd(logger, cmd, "check whether candlepin-cert-consumer-%s-1.0-1.noarch exist" % samhostname, targetmachine_ip)
			if ret == 0:
				logger.info("candlepin-cert-consumer-%s-1.0-1.noarch has already exist, remove it first." % samhostname)
				cmd = "rpm -e candlepin-cert-consumer-%s-1.0-1.noarch" % samhostname
				ret, output = self.runcmd(logger, cmd, "remove candlepin-cert-consumer-%s-1.0-1.noarch to re-register system to SAM" % samhostname, targetmachine_ip)
				if ret == 0:
					 logger.info("Succeeded to uninstall candlepin-cert-consumer-%s-1.0-1.noarch." % samhostname)
				else:
					logger.error("Failed to uninstall candlepin-cert-consumer-%s-1.0-1.noarch." % samhostname)
					self.SET_RESULT(1)
			cmd = "rpm -ivh http://%s/pub/candlepin-cert-consumer-%s-1.0-1.noarch.rpm" % (samhostip, samhostname)
			ret, output = self.runcmd(logger, cmd, "install candlepin-cert-consumer..rpm", targetmachine_ip)
			if ret == 0:
				logger.info("Succeeded to install candlepin cert and configure the system with sam configuration as %s." % samhostip)
			else:
				logger.error("Failed to install candlepin cert and configure the system with sam configuration as %s." % samhostip)
				self.SET_RESULT(1)
		elif samhostname == "subscription.rhn.stage.redhat.com":
			# configure /etc/rhsm/rhsm.conf to stage candlepin
			cmd = "sed -i -e 's/hostname = subscription.rhn.redhat.com/hostname = %s/g' /etc/rhsm/rhsm.conf" % samhostname
			ret, output = self.runcmd(logger, cmd, "configure /etc/rhsm/rhsm.conf", targetmachine_ip)
			if ret == 0:
				logger.info("Succeeded to configure rhsm.conf for stage in %s" % self.get_HG_info(targetmachine_ip))
			else:
				logger.error("Failed to configure rhsm.conf for stage in %s" % self.get_HG_info(targetmachine_ip))
				self.SET_RESULT(1)
		else:
			logger.error("Failed to configure the host")
			self.SET_RESULT(1)

	def configure_stage_host(self, logger, serverhostname, targetmachine_ip=""):
		''' configure the host machine. '''
		if serverhostname == "subscription.rhn.stage.redhat.com":
			# configure /etc/rhsm/rhsm.conf to stage candlepin
			cmd = "sed -i -e 's/hostname = subscription.rhn.redhat.com/hostname = %s/g' /etc/rhsm/rhsm.conf" % serverhostname
			ret, output = self.runcmd(logger, cmd, "configure /etc/rhsm/rhsm.conf", targetmachine_ip)
			if ret == 0:
				logger.info("Succeeded to configure rhsm.conf for stage in %s" % self.get_HG_info(targetmachine_ip))
			else:
				logger.error("Failed to configure rhsm.conf for stage in %s" % self.get_HG_info(targetmachine_ip))
				self.SET_RESULT(1)
		else:
			logger.error("Failed to configure stage host")
			self.SET_RESULT(1)

# Can't pass in RHEL5.11, will research later
#	def vw_restart_virtwho(self, logger, targetmachine_ip=""):
#		''' Restart the virt-who service. '''
#		if self.above_7_serials(logger):
#			cmd = "systemctl restart virt-who.service; sleep 10"
#			ret, output = self.runcmd(logger, cmd, "systemctl restart virt-who.service", targetmachine_ip)
#			if ret == 0:
#				logger.info("Succeeded to restart virt-who service by systemctl.")
#			else:
#				logger.error("Failed to restart virt-who service by systemctl.")
#				self.SET_RESULT(1)
#		else:
#			if targetmachine_ip == "":
#				subprocess.call("service virt-who restart; sleep 10", shell=True)
#			else:
#				cmd = "service virt-who restart; sleep 10"
#				ret, output = self.runcmd(logger, cmd, "restart virt-who", targetmachine_ip)
#				if ret == 0:
#					logger.info("Succeeded to restart virt-who service.")
#				else:
#					logger.error("Failed to restart virt-who service.")
#					self.SET_RESULT(1)

	def vw_restart_virtwho(self, logger, targetmachine_ip=""):
		''' Restart the virt-who service. '''
		if targetmachine_ip == "":
			subprocess.call("service virt-who restart; sleep 10", shell=True)
		else:
			cmd = "service virt-who restart; sleep 10"
			ret, output = self.runcmd(logger, cmd, "stop virt-who", targetmachine_ip)
			if ret == 0:
				logger.info("Succeeded to restart virt-who service.")
			else:
				logger.error("Failed to restart virt-who service.")
				self.SET_RESULT(1)

	def vw_stop_virtwho(self, logger, targetmachine_ip=""):
		''' Stop virt-who service. '''
		cmd = "service virt-who stop; sleep 10"
		ret, output = self.runcmd(logger, cmd, "stop virt-who", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to stop virt-who service.")
		else:
			logger.error("Failed to stop virt-who service.")
			self.SET_RESULT(1)
				
	def vw_check_virtwho_status(self, logger, targetmachine_ip=""):
		''' Check the virt-who status. '''
		cmd = "service virt-who status; sleep 10"
		ret, output = self.runcmd(logger, cmd, "virt-who status", targetmachine_ip)
		if self.above_7_serials(logger):
			if ret == 0 and "running" in output:
				logger.info("Succeeded to check virt-who is running.")
			else:
				logger.error("Failed to check virt-who is running.")
				self.SET_RESULT(1)
		else:
			if ret == 0 and "running" in output:
				logger.info("Succeeded to check virt-who is running.")
				self.SET_RESULT(0)
			else:
				logger.error("Failed to check virt-who is running.")
				self.SET_RESULT(1)

	def vw_check_libvirtd_status(self, logger, targetmachine_ip=""):
		''' Check the libvirtd status. '''
		cmd = "service libvirtd status; sleep 10"
		ret, output = self.runcmd(logger, cmd, "libvirtd status", targetmachine_ip)
		if self.above_7_serials(logger):
			if ret == 0 and "running" in output:
				logger.info("Succeeded to check libvirtd is running.")
			else:
				logger.error("Failed to check libvirtd is running.")
				self.SET_RESULT(1)
		else:
			if ret == 0 and "running" in output:
				logger.info("Succeeded to check libvirtd is running.")
				self.SET_RESULT(0)
			else:
				logger.error("Failed to check libvirtd is running.")
				self.SET_RESULT(1)

	def vw_restart_libvirtd(self, logger, targetmachine_ip=""):
		''' Restart the libvirtd service on host: service libvirtd restart. '''
		cmd = "service libvirtd restart; sleep 30"
		ret, output = self.runcmd(logger, cmd, "restart libvirtd", targetmachine_ip)
		if self.above_7_serials(logger):
			if ret == 0:
				logger.info("Succeeded to restart libvirtd service.")
			else:
				logger.error("Failed to restart libvirtd service.")
				self.SET_RESULT(1)
		else:
			if ret == 0 and "OK" in output:
				logger.info("Succeeded to restart libvirtd service.")
			else:
				logger.error("Failed to restart libvirtd service.")
				self.SET_RESULT(1)
				
	def vw_restart_vdsm(self, logger, targetmachine_ip=""):
		''' Restart the libvirtd service on host: service libvirtd restart. '''
		cmd = "service vdsmd restart; sleep 30"
		ret, output = self.runcmd(logger, cmd, "restart vdsmd", targetmachine_ip)
		if ret == 0 and "OK" in output:
			logger.info("Succeeded to restart vdsm service.")
		else:
			logger.error("Failed to restart vdsm service.")
			self.SET_RESULT(1)

	def vw_get_uuid(self, logger, guestname):
		''' get the guest uuid. '''
		cmd = "virsh domuuid %s" % guestname
		ret, output = self.runcmd(logger, cmd, "get virsh domuuid")
		guestuuid = output[:-1]
		return guestuuid

	def vw_check_uuid(self, logger, params, guestname, guestuuid="Default", uuidexists=True, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
		''' check if the guest uuid is correctly monitored by virt-who. '''
		if guestname != "" and guestuuid == "Default":
			guestuuid = self.vw_get_uuid(logger, guestname)
		rhsmlogfile = os.path.join(rhsmlogpath, "rhsm.log")
		self.vw_restart_virtwho(logger, targetmachine_ip)
		cmd = "tail -1 %s " % rhsmlogfile
		ret, output = self.runcmd(logger, cmd, "check output in rhsm.log")
		if ret == 0:
			''' get guest uuid.list from rhsm.log '''
			if "Sending list of uuids: " in output:
				log_uuid_list = output.split('Sending list of uuids: ')[1]
				logger.info("Succeeded to get guest uuid.list from rhsm.log.")
			elif "Sending update to updateConsumer: " in output:
				log_uuid_list = output.split('Sending list of uuids: ')[1]
				logger.info("Succeeded to get guest uuid.list from rhsm.log.")
			else:
				logger.error("Failed to get guest %s uuid.list from rhsm.log" % guestname)
				self.SET_RESULT(1)
# 			# for kvm send uuid list changes
# 			temp_list = []
# 			for item in log_uuid_list:
# 				if item.has_key("guestId"):
# 					temp_list.append(item["guestId"])
			# check guest uuid in log_uuid_list
			if uuidexists:
				if guestname == "":
					return len(log_uuid_list) == 0
				else:
					logger.info("guestuuid %s in log_uuid_list" % guestuuid)
					return (guestuuid in log_uuid_list)
			else:
				if guestname == "":
					return not len(log_uuid_list) == 0
				else:
					return not (guestuuid in log_uuid_list)
		else:
			logger.error("Failed to get uuids in rhsm.log")
			self.SET_RESULT(1)

	def vw_check_attr(self, logger, params, guestname, guest_status, guest_type, guest_hypertype, guest_state, guestuuid, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
		''' check if the guest attributions is correctly monitored by virt-who. '''
		rhsmlogfile = os.path.join(rhsmlogpath, "rhsm.log")
		self.vw_restart_virtwho(logger, targetmachine_ip)
		cmd = "tail -1 %s " % rhsmlogfile
		ret, output = self.runcmd(logger, cmd, "check output in rhsm.log")
		if ret == 0:
			''' get guest uuid.list from rhsm.log '''
			if "Sending list of uuids: " in output:
				log_uuid_list = output.split('Sending list of uuids: ')[1]
				logger.info("Succeeded to get guest uuid.list from rhsm.log.")
			elif "Sending update to updateConsumer: " in output:
				log_uuid_list = output.split('Sending list of uuids: ')[1]
				logger.info("Succeeded to get guest uuid.list from rhsm.log.")
			else:
				logger.error("Failed to get guest %s uuid.list from rhsm.log" % guestname)
				self.SET_RESULT(1)
			loglist = eval(log_uuid_list)
			for item in loglist:
				if item['guestId'] == guestuuid:
					attr_status = item['attributes']['active']
					logger.info("guest's active status is %s." % attr_status)
					attr_type = item['attributes']['virtWhoType']
					logger.info("guest virtwhotype is %s." % attr_type)
					attr_hypertype = item['attributes']['hypervisorType']
					logger.info("guest hypervisortype is %s." % attr_hypertype)
					attr_state = item['state']
					logger.info("guest state is %s." % attr_state)
			if guestname != "" and (guest_status == attr_status) and (guest_type in attr_type) and (guest_hypertype in attr_hypertype) and (guest_state == attr_state):
				logger.info("successed to check guest %s attribute" % guestname)
				return True
			else:
				logger.error("Failed to check guest %s attribute" % guestname)
				return False
		else:
			logger.error("Failed to get uuids in rhsm.log")
			self.SET_RESULT(1)

	def check_virtpid(self, logger, checkpid, checknum, targetmachine_ip=""):
		cmd = "ls /proc/%s/task/ | wc -l" %checkpid
		(ret, output) = self.runcmd(logger, cmd, "get virt-who thread num", targetmachine_ip)
		if ret == 0 and int(output) == checknum:
			logger.info("Succeeded to check the virt-who thread.")
		else:
			logger.error("Failed to check the virt-who thread.")
			self.SET_RESULT(1)
				
	def sub_check_bonus(self, logger, productid, targetmachine_ip=""):
		# List available pools of guest
		new_available_poollist = self.sub_listavailpools(logger, ee.productid_guest, targetmachine_ip)
		if new_available_poollist != None:
			bonus_pool_check = 1
			for item in range(0, len(new_available_poollist)):
				if new_available_poollist[item]["SKU"] == ee.productid_guest and self.check_type_virtual(new_available_poollist[item]) and new_available_poollist[item]["Quantity"] == ee.guestlimit:
					logger.info("Succeeded to list bonus pool of product %s" % ee.productname_guest) 
					bonus_pool_check = 0
			if bonus_pool_check == 1:
				self.SET_RESULT(1)
		else:
			logger.error("Failed to get available pool list from guest.")
			self.SET_RESULT(1)

	def check_bonus_existance(self, logger, SKU_id, targetmachine_ip="", existance=True):
		new_available_poollist = self.sub_listavailpools(logger, SKU_id, targetmachine_ip)
		if new_available_poollist != None:
			if existance:
				bonus_pool_check = 1
				for item in range(0, len(new_available_poollist)):
					if new_available_poollist[item]["SKU"] == SKU_id and self.check_type_virtual(new_available_poollist[item]):
						logger.info("Succeeded to list bonus pool of product %s" % SKU_id) 
						bonus_pool_check = 0
			else:
				bonus_pool_check = 0
				for item in range(0, len(new_available_poollist)):
					if new_available_poollist[item]["SKU"] == SKU_id and self.check_type_virtual(new_available_poollist[item]):
						logger.info("Unexpected to list bonus pool of product %s" % SKU_id) 
						bonus_pool_check = 1
			if bonus_pool_check == 1:
				self.SET_RESULT(1)
		else:
			logger.error("Failed to get available pool list from guest.")
			self.SET_RESULT(1)

	def check_datacenter_bonus_existance(self, logger, subscription_name, targetmachine_ip="", existance=True):
		new_available_poollist = self.sub_datacenter_listavailpools(logger, subscription_name, targetmachine_ip)
		if new_available_poollist != None:
			if existance:
				bonus_pool_check = 1
				for item in range(0, len(new_available_poollist)):
					if new_available_poollist[item]["SubscriptionName"] == subscription_name and self.check_type_virtual(new_available_poollist[item]):
						logger.info("Succeeded to list bonus pool of product %s" % subscription_name) 
						bonus_pool_check = 0
			else:
				bonus_pool_check = 0
				for item in range(0, len(new_available_poollist)):
					if new_available_poollist[item]["SubscriptionName"] == subscription_name and self.check_type_virtual(new_available_poollist[item]):
						logger.error("Unexpected to list bonus pool of product %s" % subscription_name) 
						bonus_pool_check = 1
			if bonus_pool_check == 1:
				self.SET_RESULT(1)
		else:
			logger.error("Failed to get available pool list from guest.")
			self.SET_RESULT(1)

	def check_bonus_attribute(self, logger, subscription_name, attribute_key, attribute_value, targetmachine_ip=""):
		new_available_poollist = self.sub_datacenter_listavailpools(logger, subscription_name, targetmachine_ip)
		if new_available_poollist != None:
			check_result = 1
			for item in range(0, len(new_available_poollist)):
				if attribute_key == "Available":
					if "Quantity" in new_available_poollist[item]:
						attribute_key = "Quantity"
				if new_available_poollist[item]["SubscriptionName"] == subscription_name and self.check_type_virtual(new_available_poollist[item]):
					if new_available_poollist[item][attribute_key] == attribute_value:
						logger.info("Succeeded to check_bonus_attribute %s is: %s" % (attribute_key, attribute_value))
						check_result = 0
			if check_result == 1:
				self.SET_RESULT(1)
		else:
			logger.error("Failed to get available pool list from guest.")
			self.SET_RESULT(1)

	def setup_custom_facts(self, logger, facts_key, facts_value, targetmachine_ip=""):
		''' setup_custom_facts '''
		cmd = "echo '{\"" + facts_key + "\":\"" + facts_value + "\"}' > /etc/rhsm/facts/custom.facts"
		ret, output = self.runcmd(logger, cmd, "create custom.facts", targetmachine_ip)
		if ret == 0 :
			logger.info("Succeeded to create custom.facts %s." % self.get_HG_info(targetmachine_ip))
		else:
			logger.error("Failed to create custom.facts %s." % self.get_HG_info(targetmachine_ip))
			self.SET_RESULT(1)

		cmd = "subscription-manager facts --update"
		ret, output = self.runcmd(logger, cmd, "update subscription facts", targetmachine_ip)
		if ret == 0 and "Successfully updated the system facts" in output:
			logger.info("Succeeded to update subscription facts %s." % self.get_HG_info(targetmachine_ip))
		else:
			logger.error("Failed to update subscription facts %s." % self.get_HG_info(targetmachine_ip))
			self.SET_RESULT(1)

	def restore_facts(self, logger, targetmachine_ip=""):
		''' setup_custom_facts '''
		cmd = "rm -f /etc/rhsm/facts/custom.facts"
		ret, output = self.runcmd(logger, cmd, "remove custom.facts", targetmachine_ip)
		if ret == 0 :
			logger.info("Succeeded to remove custom.facts %s." % self.get_HG_info(targetmachine_ip))
		else:
			logger.error("Failed to remove custom.facts %s." % self.get_HG_info(targetmachine_ip))
			self.SET_RESULT(1)

		cmd = "subscription-manager facts --update"
		ret, output = self.runcmd(logger, cmd, "update subscription facts", targetmachine_ip)
		if ret == 0 and "Successfully updated the system facts" in output:
			logger.info("Succeeded to update subscription facts %s." % self.get_HG_info(targetmachine_ip))
		else:
			logger.error("Failed to update subscription facts %s." % self.get_HG_info(targetmachine_ip))
			self.SET_RESULT(1)

	def vw_define_all_guests(self, logger, testtype, params, targetmachine_ip=""):
		if testtype == "kvm":
			for guestname in ee().get_all_guests_list(ee.imagepath_kvm):
				params["guesttype"] = "kvm"
				params["fullimagepath"] = os.path.join(ee.imagepath_kvm, guestname)
				self.vw_define_guest(logger, params, guestname)
		elif testtype == "xen":
			for guestname in ee().get_all_guests_list(ee.imagepath_xen_pv):
				params["guesttype"] = "xenpv"
				params["fullimagepath"] = os.path.join(ee.imagepath_xen_pv, guestname)
				self.vw_define_guest(logger, params, guestname)
			for guestname in ee().get_all_guests_list(ee.imagepath_xen_fv):
				params["guesttype"] = "xenfv"
				params["fullimagepath"] = os.path.join(ee.imagepath_xen_fv, guestname)
				self.vw_define_guest(logger, params, guestname)

	def vw_define_guest(self, logger, params, guestname, targetmachine_ip=""):
		''' Define a guest in host machine. '''
		cmd = "virsh list --all"
		ret, output = self.runcmd(logger, cmd, "list all guest", "", False)
		if not guestname + " " in output:
			params["guestname"] = guestname
			self.set_guestpath_guesttype(guestname, params)
			params["ifacetype"] = "bridge"
			params["source"] = "switch"
			if define.define(params) == 0:
				logger.info("Succeeded to define the guest '%s' in host machine.\n" % guestname)
			else:
				logger.error("Failed to define the guest '%s' in host machine.\n" % guestname)
			ret, output = self.runcmd(logger, cmd, "list all guest", targetmachine_ip)

	def vw_force_define_guest(self, logger, params, guestname, targetmachine_ip=""):
		''' Define a guest in host machine. '''
		cmd = "virsh list --all"
		ret, output = self.runcmd(logger, cmd, "list all guest", "", True)
		if output is not "":
			params["guestname"] = guestname
			self.set_guestpath_guesttype(guestname, params)
			params["ifacetype"] = "bridge"
			params["source"] = "switch"
			if define.define(params) == 0:
				logger.info("Succeeded to define the guest '%s' in host machine.\n" % guestname)
			else:
				logger.error("Failed to define the guest '%s' in host machine.\n" % guestname)
			ret, output = self.runcmd(logger, cmd, "list all guest", targetmachine_ip)

	def set_guestpath_guesttype(self, guestname, params):
		''' set fullimagepath and guesttype for define guest '''
		if "PV" in guestname:
			params["guesttype"] = "xenpv"
			params["fullimagepath"] = os.path.join(ee.imagepath_xen_pv, guestname)
		elif "FV" in guestname:
			params["guesttype"] = "xenfv"
			params["fullimagepath"] = os.path.join(ee.imagepath_xen_fv, guestname)
		else:
			params["guesttype"] = "kvm"
			params["fullimagepath"] = os.path.join(ee.imagepath_kvm, guestname)

	def vw_start_guest(self, logger, params, guestname):
		''' Start a guest in host machine. '''
		cmd = "virsh list --all"
		ret, output = self.runcmd(logger, cmd, "list all guest", "", False)
		if guestname + " " in output:
			params["guestname"] = guestname
			if start.start(params) == 0:
				logger.info("Succeeded to start the guest '%s' in host machine." % guestname)
				time.sleep(20)
			else:
				logger.error("Failed to start the guest '%s' in host machine." % guestname)
				self.vw_destroy_guest(logger, params, guestname)
				self.SET_RESULT(1)
		else:
			logger.error("The guest '%s' is not in host machine, can not do start." % guestname)
			self.SET_RESULT(1)

	def vw_pause_guest(self, logger, params, guestname):
		''' Pause a guest in host machine. '''
		cmd = "virsh list --all"
		ret, output = self.runcmd(logger, cmd, "list all guest", "", False)
		if guestname + " " in output:
			params["guestname"] = guestname
			if suspend.suspend(params) == 0:
				logger.info("Succeeded to pause the guest '%s' in host machine." % guestname)
			else:
				logger.error("Failed to pause the guest '%s' in host machine." % guestname)
				self.vw_destroy_guest(logger, params, guestname)
				self.SET_RESULT(1)
		else:
			logger.error("The guest '%s' is not in host machine, can not do pause." % guestname)
			self.SET_RESULT(1)

	def vw_resume_guest(self, logger, params, guestname):
		''' Resume a guest in host machine. '''
		cmd = "virsh list --all"
		ret, output = self.runcmd(logger, cmd, "list all guest", "", False)
		if guestname + " " in output:
			params["guestname"] = guestname
			if resume.resume(params) == 0:
				logger.info("Succeeded to resume the guest '%s' in host machine." % guestname)
			else:
				logger.error("Failed to resume the guest '%s' in host machine." % guestname)
				self.vw_destroy_guest(logger, params, guestname)
				self.SET_RESULT(1)
		else:
			logger.error("The guest '%s' is not in host machine, can not do resume." % guestname)
			self.SET_RESULT(1)

	def vw_shutdown_guest(self, logger, params, guestname):
		''' Shutdown a guest in host machine. '''
		cmd = "virsh list --all"
		ret, output = self.runcmd(logger, cmd, "list all guest", "", False)
		if guestname + " " in output:
			params["guestname"] = guestname
			if shutdown.shutdown(params) == 0:
				logger.info("Succeeded to shutdown the guest '%s' in host machine." % guestname)
			else:
				logger.info("shutdown guest is failed, try to do destroy to the guest '%s'" % guestname)
				self.vw_destroy_guest(logger, params, guestname)
				self.SET_RESULT(1)
		else:
			logger.error("The guest '%s' is not in host machine, can not do shutdown." % guestname)
			self.SET_RESULT(1)

	def vw_destroy_guest(self, logger, params, guestname):
		''' Destory a guest in host machine. '''
		cmd = "virsh list --all"
		ret, output = self.runcmd(logger, cmd, "list all guest", "", False)
		if guestname + " " in output:
			params["guestname"] = guestname
			if destroy.destroy(params) == 0:
				logger.info("Succeeded to destroy the guest '%s' in host machine." % guestname)
				ret, output = self.runcmd(logger, cmd, "list all guest after destory guest %s." % guestname)
			else:
				logger.error("Failed to destroy the guest '%s' in host machine." % guestname)
				self.SET_RESULT(1)
		else:
			logger.error("The guest '%s' is not in host machine, can not do destroy." % guestname)
			self.SET_RESULT(1)

	def vw_undefine_guest(self, logger, params, guestname):
		''' Undefine a guest in host machine. '''
		cmd = "virsh list --all"
		ret, output = self.runcmd(logger, cmd, "list all guest", "", False)
		if guestname + " " in output:
			params["guestname"] = guestname
			if undefine.undefine(params) == 0:
				logger.info("Succeeded to undefine the guest '%s' in host machine." % guestname)
				ret, output = self.runcmd(logger, cmd, "list all guest after undefine guest.")
			else:
				logger.error("Failed to undefine the guest '%s' in host machine." % guestname)
				self.SET_RESULT(1)
		else:
			logger.error("Failed to undefine the guest '%s' which is not defined in host machine." % guestname)
			self.SET_RESULT(1)

	def vw_undefine_all_guests(self, logger, params):
		''' Undefine all guests in host machine. '''
		cmd = "virsh list --all"
		ret, output = self.runcmd(logger, cmd, "list all guest", "", False)
		# get guest list by parse output
		datalines = output.splitlines()
		guest_list = []
		for line in datalines:
			if " -     " in line:
				guest_list.append(line.split(" ")[6])
		for item in guest_list:
			self.vw_undefine_guest(logger, params, item)
		ret, output = self.runcmd(logger, cmd, "list all guest after undefine all guests.")
# 		srcuri = utils().get_uri("127.0.0.1")
# 		conn = connectAPI.ConnectAPI()
# 		src = conn.open(srcuri)
# 		srcdom = DomainAPI(src)
# 		guest_names = srcdom.get_list()
# 		guest_names += srcdom.get_defined_list()
# 		logger.info("All defined guests [total: %d]: " % len(guest_names) + ", ".join(guest_names))
# 		if len(guest_names) != 0:
# 			for guestname in guest_names:
# 				if (guestname in ee.guestnamekcol) or (guestname in ee.guestnamepcol) or (guestname in ee.guestnamefcol):
# 					gueststate = srcdom.get_state(guestname)
# 					if  gueststate == 'running' or gueststate == 'blocked' or gueststate == 'paused':
# 						if self.vw_destroy_guest(logger, params, guestname):
# 							src.close()
# 							logger.info("close local hypervisor connection")
# 							logger.error("Failed to destroy the guest '%s' when try to undefine all the guests." % guestname)
# 			
# 					if self.vw_undefine_guest(logger, params, guestname):
# 						src.close()
# 						logger.info("close local hypervisor connection")
# 						self.SET_RESULT(1)
# 				else:
# 					logger.info("The guest '%s' is not in test scope so not handled when try to undefine all the guests." % guestname)
#
# 			logger.info("Succeeded to undefine all the %d guests in host machine: %s" % (len(guest_names), ", ".join(guest_names)))
# 		else:
# 			logger.info("There is no any guest to undefine in host machine, so no action happens to undefine all guests.")
# 		
# 		src.close()
# 		logger.info("close local hypervisor connection")	
# 		return 0

	def vw_migrate_guest(self, logger, params, guestname, targetmachine_ip):
		''' Migrate a guest from source machine to target machine. '''
		cmd = "virsh list --all"
		ret, output = self.runcmd(logger, cmd, "list all guest", "", False)
		if guestname + " " in output:
			params['transport'] = "ssh"
			params['target_machine'] = targetmachine_ip
			params['username'] = "root"
			if "redhat.com" in targetmachine_ip:
				# run in beaker
				params['password'] = "red2015"
			else:
				params['password'] = "redhat"
			params["guestname"] = guestname
			params['flags'] = "live"
			'''
			params['poststate']="running"
			params['presrcconfig']="false"
			params['postsrcconfig']="false"
			params['predstconfig']="false"
			params['postdstconfig']="true"
			'''
			if migrate.migrate(params) == 0:
				logger.info("Succeeded to migrate the guest '%s'." % guestname)
				ret, output = self.runcmd(logger, cmd, "list all guest after migrate guest %s" % guestname)
			else:
				logger.error("Failed to migrate the guest '%s'." % guestname)
				self.SET_RESULT(1)
		else:
			logger.error("The guest '%s' is not in host machine, can not do migrate." % guestname)
			self.SET_RESULT(1)
		self.vw_undefine_guest(logger, params, guestname)

	def vw_migrate_guest_by_cmd(self, logger, guestname, migratetargetmachine_ip, targetmachine_ip=""):
		''' migrate a guest from source machine to target machine. '''
		uri = utils().get_uri(migratetargetmachine_ip)
		cmd = "virsh migrate --live %s %s --undefinesource" % (guestname, uri)
		ret, output = self.runcmd(logger, cmd, "migrate the guest in host 2", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to migrate the guest '%s'." % guestname)
		else:
			logger.error("Failed to migrate the guest '%s'." % guestname)
			self.SET_RESULT(1)

	def vw_undefine_guest_by_cmd(self, logger, guestname, targetmachine_ip=""):
		''' Undefine a guest in host machine. '''
		cmd = "virsh undefine %s" % guestname
		ret, output = self.runcmd(logger, cmd, "undefine guest in %s" % targetmachine_ip, targetmachine_ip)
		if "Domain %s has been undefined" % guestname in output:
			logger.info("Succeeded to undefine the guest '%s' in machine %s." % (guestname, targetmachine_ip))
		else:
			logger.error("Failed to undefine the guest '%s' in machine %s." % (guestname, targetmachine_ip))
			self.SET_RESULT(1)
	#========================================================
	# 	3. Common Setup Functions
	#========================================================

	def set_cpu_socket(self, logger, cpu_socket=1, targetmachine_ip=""):
		''' To set cpu socket in configure file /etc/rhsm/facts/custom.facts. '''
		cmd = """echo \"{\\"cpu.cpu_socket(s)\\":%s}\">/etc/rhsm/facts/custom.facts""" % (cpu_socket)
		ret, output = self.runcmd(logger, cmd, "set cpu socket", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to setting cpu socket.")
		else:
			logger.error("Failed to setting cpu socket.")
			self.SET_RESULT(1)

	def copy_images(self, logger, testtype, mount_point, image_machine_imagepath, imagepath):
		''' copy the images from the image source machine. '''
		if not os.path.exists(imagepath):
			os.makedirs(imagepath)
			logger.info("Created the dir '%s'." % imagepath)

		tmpimagepath = "/tmp/entimages" + time.strftime('%Y%m%d%H%M%S')
		os.makedirs(tmpimagepath)
		logger.info("Dir '%s' has been created for copy guest image to host." % tmpimagepath)

		cmd = "mount -r %s %s" % (mount_point, tmpimagepath)
		ret, output = self.runcmd(logger, cmd, "mount images in host")
		if ret == 0:
			logger.info("Succeeded to mount images machine %s." % mount_point)
		else:
			logger.error("Failed to mount images machine %s." % mount_point)

		logger.info("Begin to copy guest images...")

		imagesrcpath = os.path.join(tmpimagepath, os.path.join(image_machine_imagepath, testtype))
		imagetgtpath = imagepath
		cmd = "cp -rf %s %s" % (imagesrcpath, imagetgtpath)
		ret, output = self.runcmd(logger, cmd, "copy images")
		if ret == 0:
			logger.info("Succeeded to copy guest images to host machine.")
		else:
			logger.error("Failed to copy guest images to host machine.")
			self.SET_RESULT(1)

		if os.path.ismount(tmpimagepath):
			cmd = "umount -f %s" % (tmpimagepath)
			ret, output = self.runcmd(logger, cmd, "unmount images in host")
			if ret == 0:
				logger.info("Succeeded to unmount images machine %s." % mount_point)
			else:
				logger.error("Failed to unmount images machine %s." % mount_point)

		os.removedirs(tmpimagepath)
		logger.info("Removed the dir '%s'." % tmpimagepath)

	def wget_images(self, logger, wget_url, guest_name, destination_ip):
		''' wget guest images '''
		# check whether guest has already been downloaded, if yes, unregister it from ESX and delete it from local
		cmd = "[ -d /vmfs/volumes/datastore*/%s ] ; echo $?" % guest_name
		ret, output = self.runcmd_byuser(logger, cmd, "check whether guest %s has been installed" % guest_name, destination_ip)
		if output == 0:
			logger.info("guest '%s' has been installed, remove it and re-install it next" % guest_name)
			# self.unregister_esx_guest()
			cmd = "rm -rf /vmfs/volumes/datastore*/%s" % guest_name
			ret, output = self.runcmd_byuser(logger, cmd, "remove guests %s" % guest_name, destination_ip)
			if ret == 0:
				logger.info("Succeeded to remove the guest '%s'." % guest_name)
			else:
				logger.error("Failed to remove the guest '%s'." % guest_name)
				self.SET_RESULT(1)
		else:
			logger.info("guest '%s' has not been installed yet, will install it next." % guest_name)
		# wget guest
		cmd = "wget -P /vmfs/volumes/datastore* %s%s.tar.gz" % (wget_url, guest_name)
		ret, output = self.runcmd_byuser(logger, cmd, "wget guests", destination_ip)
		if ret == 0:
			logger.info("Succeeded to wget the guest '%s'." % guest_name)
		else:
			logger.error("Failed to wget the guest '%s'." % guest_name)
			self.SET_RESULT(1)
		# uncompress guest and remove .gz file
		cmd = "tar -zxvf /vmfs/volumes/datastore*/%s.tar.gz -C /vmfs/volumes/datastore*/ && rm -f /vmfs/volumes/datastore*/%s.tar.gz" % (guest_name, guest_name)
		ret, output = self.runcmd_byuser(logger, cmd, "uncompress guest", destination_ip)
		if ret == 0:
			logger.info("Succeeded to uncompress guest '%s'." % guest_name)
		else:
			logger.error("Failed to uncompress guest '%s'." % guest_name)
			self.SET_RESULT(1)

	def export_dir_as_nfs(self, logger, nfs_dir, targetmachine_ip=""):
		''' export a dir as nfs '''
		cmd = "sed -i '/%s/d' /etc/exports; echo '%s *(rw,no_root_squash)' >> /etc/exports" % (nfs_dir.replace('/', '\/'), nfs_dir)
		ret, output = self.runcmd(logger, cmd, "set exporting destination dir", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to add '%s *(rw,no_root_squash)' to /etc/exports file." % nfs_dir)
		else:
			logger.error("Failed to add '%s *(rw,no_root_squash)' to /etc/exports file." % nfs_dir)
			self.SET_RESULT(1)
		cmd = "service nfs restart; sleep 10"
		ret, output = self.runcmd(logger, cmd, "restarting nfs service", targetmachine_ip)
		if ret == 0 :
			logger.info("Succeeded to restart service nfs.")
		else:
			logger.error("Failed to restart service nfs.")
			self.SET_RESULT(1)
		cmd = "rpc.mountd"
		ret, output = self.runcmd(logger, cmd, "rpc.mountd", targetmachine_ip)
		cmd = "showmount -e 127.0.0.1"
		ret, output = self.runcmd(logger, cmd, "showmount", targetmachine_ip)
		if ret == 0 and (nfs_dir in output):
			logger.info("Succeeded to export dir '%s' as nfs." % nfs_dir)
		else:
			logger.error("Failed to export dir '%s' as nfs." % nfs_dir)
			self.SET_RESULT(1)

	def mount_images_in_sourcemachine(self, logger, imagenfspath, imagepath):
		''' mount the images of the image source machine in the source machine. '''
		# create image path in source machine
		cmd = "test -d %s" % (imagepath)
		ret, output = self.runcmd(logger, cmd, "check images path in source machine")
		if ret != 0:
			cmd = "mkdir -p %s" % (imagepath)
			ret, output = self.runcmd(logger, cmd, "create image path in the source machine")
			if ret == 0 or "/home/ENT_TEST_MEDIUM/images is busy or already mounted" in output:
				logger.info("Succeeded to create imagepath in the source machine.")
			else:
				logger.error("Failed to create imagepath in the source machine.")
				self.SET_RESULT(1)

		# mount image path of source machine into just created image path in target machine
		sourcemachine_ip = utils().get_ip_address("switch")
		cmd = "mount %s:%s %s" % (sourcemachine_ip, imagenfspath, imagepath)
		ret, output = self.runcmd(logger, cmd, "mount nfs images in host machine")
		if ret == 0 or "is busy or already mounted" in output:
			logger.info("Succeeded to mount nfs images in host machine.")
		else:
			logger.error("Failed to mount nfs images in host machine.")
			self.SET_RESULT(1)

	def update_vw_configure(self, logger, background=1, debug=1, targetmachine_ip=""):
		''' update virt-who configure file /etc/sysconfig/virt-who. '''
		# cmd = "sed -i -e 's/VIRTWHO_BACKGROUND=.*/VIRTWHO_BACKGROUND=%s/g' -e 's/VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' /etc/sysconfig/virt-who" % (background, debug)
		# VIRTWHO_BACKGROUND removed from configure file
		cmd = "sed -i -e 's/VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' /etc/sysconfig/virt-who" % (debug)
		ret, output = self.runcmd(logger, cmd, "updating virt-who configure file", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to update virt-who configure file.")
		else:
			logger.error("Failed to update virt-who configure file.")
			self.SET_RESULT(1)

	def update_esx_vw_configure(self, logger, esx_owner, esx_env, esx_server, esx_username, esx_password, background=1, debug=1):
		''' update virt-who configure file /etc/sysconfig/virt-who. '''
		# cmd = "sed -i -e 's/VIRTWHO_BACKGROUND=.*/VIRTWHO_BACKGROUND=%s/g' -e 's/VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' -e 's/#VIRTWHO_ESX=.*/VIRTWHO_ESX=1/g' -e 's/#VIRTWHO_ESX_OWNER=.*/VIRTWHO_ESX_OWNER=%s/g' -e 's/#VIRTWHO_ESX_ENV=.*/VIRTWHO_ESX_ENV=%s/g' -e 's/#VIRTWHO_ESX_SERVER=.*/VIRTWHO_ESX_SERVER=%s/g' -e 's/#VIRTWHO_ESX_USERNAME=.*/VIRTWHO_ESX_USERNAME=%s/g' -e 's/#VIRTWHO_ESX_PASSWORD=.*/VIRTWHO_ESX_PASSWORD=%s/g' /etc/sysconfig/virt-who" % (background, debug, esx_owner, esx_env, esx_server, esx_username, esx_password)
		cmd = "sed -i -e 's/VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' -e 's/#VIRTWHO_ESX=.*/VIRTWHO_ESX=1/g' -e 's/#VIRTWHO_ESX_OWNER=.*/VIRTWHO_ESX_OWNER=%s/g' -e 's/#VIRTWHO_ESX_ENV=.*/VIRTWHO_ESX_ENV=%s/g' -e 's/#VIRTWHO_ESX_SERVER=.*/VIRTWHO_ESX_SERVER=%s/g' -e 's/#VIRTWHO_ESX_USERNAME=.*/VIRTWHO_ESX_USERNAME=%s/g' -e 's/#VIRTWHO_ESX_PASSWORD=.*/VIRTWHO_ESX_PASSWORD=%s/g' /etc/sysconfig/virt-who" % (debug, esx_owner, esx_env, esx_server, esx_username, esx_password)
		ret, output = self.runcmd(logger, cmd, "updating virt-who configure file")
		if ret == 0:
			logger.info("Succeeded to update virt-who configure file.")
		else:
			logger.error("Failed to update virt-who configure file.")
			self.SET_RESULT(1)

	def __parse_avail_hosts(self, logger, output):
		datalines = output.splitlines()
		pool_list = []
		data_segs = []
		segs = []
		for line in datalines:
			if "id:" in line:
				segs.append(line)
			elif segs:
				segs.append(line)
			if "name:" in line:
				data_segs.append(segs)
				segs = []

		# handle item with multi rows
		for seg in data_segs:
			length = len(seg)
			for index in range(0, length):
				if ":" not in seg[index]:
					seg[index - 1] = seg[index - 1] + " " + seg[index].strip()
			for item in seg:
				if ":" not in item:
					seg.remove(item)

		# parse detail information for each pool
		for seg in data_segs:
			pool_dict = {}
			for item in seg:
				keyitem = item.split(":")[0].replace(" ", "")
				valueitem = item.split(":")[1].strip()
				pool_dict[keyitem] = valueitem
			pool_list.append(pool_dict)
		return pool_list

	def sub_listavailhosts(self, logger, hostname, targetmachine_ip=""):
		''' List available pools.'''
		self.enter_rhevm_shell(logger, targetmachine_ip)
		cmd = "list hosts"
		ret, output = self.runcmd(logger, cmd, "list all hosts in rhevm")
		if ret == 0:
			if "name" in output:
				if id in output:
					logger.info("Succeeded to list the hosts %s." % self.get_HG_info(targetmachine_ip))
					pool_list = self.__parse_avail_hosts(logger, output)
					return pool_list
				else:
					logger.error("Failed to list the hosts %s." % self.get_HG_info(targetmachine_ip))
					self.SET_RESULT(1)
			else:
				logger.error("Failed to list the hosts %s. - There is no hosts to list!" % self.get_HG_info(targetmachine_ip))
				self.SET_RESULT(1)
		else:
			logger.error("Failed to list hosts %s." % self.get_HG_info(targetmachine_ip))
			self.SET_RESULT(1)

	def kvm_wget_xml_file(self, logger, targetmachine_ip=""):
		''' wget xml for define guest: virsh define kvm_auto_guest.xml.'''
		cmd = "wget -P /tmp/ http://10.66.100.116/projects/sam-virtwho/kvm_auto_guest.xml"
		ret, output = self.runcmd(logger, cmd, "wget kvm xml file", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to wget xml img file")
		else:
			logger.error("Failed to wget xml img file")
			self.SET_RESULT(1)

	def kvm_create_dummy_guest(self, logger, guest_name, destination_ip=""):
		''' create dummy guest in kvm '''
		cmd = "sed -i -e 's/kvm_auto_guest_[0-9]*/%s/g' /tmp/kvm_auto_guest.xml" % guest_name
		ret, output = self.runcmd(logger, cmd, "Set kvm auto guest name to %s" % guest_name, destination_ip)
		# if ret == 0:
		# 	logger.info("Succeeded to set kvm auto guest name %s" % guest_name)
		# else:
		# 	logger.error("Failed to set kvm auto guest name %s" % guest_name)
		# 	self.SET_RESULT(1)
		cmd = "virsh define /tmp/kvm_auto_guest.xml"
		ret, output = self.runcmd(logger, cmd, "define kvm auto guest: %s" % guest_name, destination_ip)
		if ret == 0:
			logger.info("Succeeded to define kvm auto guest: %s" % guest_name)
		else:
			logger.error("Failed to define kvm auto guest: %s" % guest_name)
			self.SET_RESULT(1)

	def kvm_get_guest_uuid(self, logger, guest_name, destination_ip=""):
		''' kvm_get_guest_uuid '''
		cmd = "virsh domuuid %s" % guest_name
		ret, output = self.runcmd(logger, cmd, "get kvm auto guest uuid: %s" % guest_name, destination_ip)
		if ret == 0:
			logger.info("Succeeded to get kvm auto guest uuid: %s" % guest_name)
			return output.strip()
		else:
			logger.error("Failed to get kvm auto guest uuid: %s" % guest_name)
			self.SET_RESULT(1)

	def kvm_remove_guest(self, logger, guest_name, destination_ip=""):
		''' kvm_remove_guest '''
		cmd = "virsh undefine %s" % guest_name
		ret, output = self.runcmd(logger, cmd, "remove kvm auto guest: %s" % guest_name, destination_ip)
		time.sleep(1)
		if ret == 0:
			logger.info("Succeeded to remove kvm auto guest: %s" % guest_name)
			return output.strip()
		else:
			logger.error("Failed to remove kvm auto guest: %s" % guest_name)
			self.SET_RESULT(1)

	#========================================================
	# 	4. Migration Functions
	#========================================================

	def mount_images_in_targetmachine(self, logger, targetmachine_ip, imagenfspath, imagepath):
		''' mount the images of the image source machine in the target machine. '''
		cmd = "test -d %s" % (imagepath)
		ret, output = self.runcmd(logger, cmd, "check images dir exist", targetmachine_ip)
		if ret == 1:
			cmd = "mkdir -p %s" % (imagepath)
			ret, output = self.runcmd(logger, cmd, "create image path in the target machine", targetmachine_ip)
			if ret == 0:
				logger.info("Succeeded to create imagepath in the target machine.")
			else:
				logger.error("Failed to create imagepath in the target machine.")
				self.SET_RESULT(1)
		# mount image path of source machine into just created image path in target machine
		sourcemachine_ip = utils().get_ip_address("switch")
		cmd = "mount %s:%s %s" % (sourcemachine_ip, imagenfspath, imagepath)
		ret, output = self.runcmd(logger, cmd, "mount images in the target machine", targetmachine_ip)
		if ret == 0 or "is busy or already mounted" in output:
			logger.info("Succeeded to mount images in the target machine.")
		else:
			logger.error("Failed to mount images in the target machine.")
			self.SET_RESULT(1)

	def mount_rhsmlog_of_targetmachine(self, logger, targetmachine_ip, rhsmlog_for_targetmachine):
		''' mount the rhsm log of the target machine into source machine. '''
		# create the dir rhsmlog_for_targetmachine
		# if not os.path.exists(rhsmlog_for_targetmachine):
		# 	os.makedirs(rhsmlog_for_targetmachine)
		# 	logger.info("Created the dir '%s'." % rhsmlog_for_targetmachine)
		cmd = "test -d %s" % (rhsmlog_for_targetmachine)
		ret, output = self.runcmd(logger, cmd, "check rhsmlog nfs dir exist")
		if ret != 0:
			cmd = "mkdir -p %s" % (rhsmlog_for_targetmachine)
			ret, output = self.runcmd(logger, cmd, "create rhsmlog nfs dir in source machine")
			if ret == 0:
				logger.info("Succeeded to create rhsmlog nfs dir.")
			else:
				logger.error("Failed to create rhsmlog nfs dir.")
				self.SET_RESULT(1)
		self.export_dir_as_nfs(logger, "/var/log/rhsm", targetmachine_ip)
		if os.path.ismount(rhsmlog_for_targetmachine):
			logger.info("The rhsm log of target machine has already been mounted in '%s'." % rhsmlog_for_targetmachine)
		else:
			# mount the rhsm log of target machine into the dir rhsmlog_for_targetmachine
			cmd = "mount -r %s:%s %s" % (targetmachine_ip, "/var/log/rhsm/", rhsmlog_for_targetmachine)
			ret, output = self.runcmd(logger, cmd, "mount the rhsm log dir of target machine")
			if ret == 0:
				logger.info("Succeeded to mount the rhsm log dir of target machine.")
			else:
				logger.error("Failed to mount the rhsm log dir of target machine.")
				self.SET_RESULT(1)

	def update_hosts_file(self, logger, targetmachine_ip, targetmachine_hostname):
		''' update /etc/hosts file with the host name/ip and migration destination host name/ip. '''
		# (1)add target machine hostip and hostname in /etc/hosts of source machine
		cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (targetmachine_ip, targetmachine_ip, targetmachine_hostname)
		logger.info(cmd)
		ret, output = self.runcmd(logger, cmd, "adding hostip hostname to /etc/hosts of source machine")
		if ret == 0:
			logger.info("Succeeded to add %s %s to /etc/hosts of source machine." % (targetmachine_ip, targetmachine_hostname))
		else:
			logger.error("Failed to add %s %s to /etc/hosts of source machine." % (targetmachine_ip, targetmachine_hostname))
			self.SET_RESULT(1)
		# (2)add source machine hostip and hostname in /etc/hosts of target machine
		sourcemachine_ip = utils().get_ip_address("switch")
		sourcemachine_hostname = utils().get_local_hostname()
		cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (sourcemachine_ip, sourcemachine_ip, sourcemachine_hostname)
		ret, output = self.runcmd(logger, cmd, "adding hostip hostname to /etc/hosts of target machine", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to add hostip %s and hostname %s in /etc/hosts of target machine." % (sourcemachine_ip, sourcemachine_hostname))
		else:
			logger.error("Failed to add hostip %s and hostname %s in /etc/hosts of target machine." % (sourcemachine_ip, sourcemachine_hostname))
			self.SET_RESULT(1)

	def stop_firewall(self, logger, targetmachine_ip=""):
		''' Stop iptables service and setenforce as 0. '''
		# stop iptables service
		cmd = "service iptables stop; sleep 20"
		ret, output = self.runcmd(logger, cmd, "Stop iptables service", targetmachine_ip)
		cmd = "service iptables status; sleep 10"
		ret, output = self.runcmd(logger, cmd, "Chech iptables service status", targetmachine_ip)
		if ("Firewall is stopped" in output) or ("Firewall is not running" in output) or ("Active: inactive" in output):
			logger.info("Succeeded to stop iptables service.")
		else:
			logger.error("Failed to stop iptables service.")
			self.SET_RESULT(1)
		# setenforce as 0
		cmd = "setenforce 0"
		ret, output = self.runcmd(logger, cmd, "Set setenforce 0", targetmachine_ip)
		cmd = "getenforce"
		ret, output = self.runcmd(logger, cmd, "Get setenforce 0", targetmachine_ip)
		if ret == 0 and "Permissive" in output:
			logger.info("Succeeded to setenforce as 0.")
		else:
			logger.error("Failed to setenforce as 0.")
			self.SET_RESULT(1)

	def update_xen_configure(self, logger, targetmachine_ip=""):
		''' update xen configuration file /etc/xen/xend-config.sxp for migration to 
			make sure contain necessary config options, and then restart service xend.
		'''
		# (1)update xen configuration file /etc/xen/xend-config.sxp
		expr1 = "'s/#(xend-relocation-server no)/(xend-relocation-server yes)/'"
		expr2 = "'s/#(xend-relocation-port 8002)/(xend-relocation-port 8002)/'"
		expr3 = "\"s/#(xend-relocation-address '')/(xend-relocation-address '')/\""
		expr4 = "\"s/#(xend-relocation-hosts-allow '')/(xend-relocation-hosts-allow '')/\""
		cmd = "sed  -i -e %s -e %s -e %s -e %s /etc/xen/xend-config.sxp" % (expr1, expr2, expr3, expr4)
		if targetmachine_ip == "":
			(ret, output) = commands.getstatusoutput(cmd)
		else:
			(ret, output) = utils().remote_exec_pexpect(targetmachine_ip, "root", "redhat", cmd)
		logger.info(" [command] of updating xen configuration file /etc/xen/xend-config.sxp: \n%s" % cmd)
		logger.info(" [result ] of updating xen configuration file /etc/xen/xend-config.sxp: %s" % str(ret))
		logger.info(" [output ] of updating xen configuration file /etc/xen/xend-config.sxp: \n%s" % str(output))
		if ret:
			logger.error("Failed to updating xen configuration file /etc/xen/xend-config.sxp.")
			self.SET_RESULT(1)
		else:
			logger.info("Succeeded to updating xen configuration file /etc/xen/xend-config.sxp.")
			
		# (2)restart service xend.
		cmd = "service xend restart; sleep 10"
		if targetmachine_ip == "":
			(ret, output) = commands.getstatusoutput(cmd)
		else:
			(ret, output) = utils().remote_exec_pexpect(targetmachine_ip, "root", "redhat", cmd)
		time.sleep(3)  # wait some time for service xend restart
		logger.info(" [command] of restart xend service: %s" % cmd)
		logger.info(" [result ] of restart xend service: %s" % str(ret))
		logger.info(" [output ] of restart xend service: \n%s" % str(output))
		if ret:
			logger.error("Failed to restart xend service.")
			self.SET_RESULT(1)
		else:
			logger.info("Succeeded to restart xend service.")
			return 0

	def unmount_imagepath_in_sourcemachine(self, logger, imagepath):
		''' unmount the image path in the source machine. '''
		cmd = "mount"
		ret, output = self.runcmd(logger, cmd, "showing mount point in source machine")
		if "on %s type nfs" % (imagepath) in output:
			cmd = "umount -f %s" % (imagepath)
			ret, output = self.runcmd(logger, cmd, "unmount the image path in source machine")
			if ret == 0:
				logger.info("Succeeded to unmount the image path in source machine.")
			else:
				logger.error("Failed to unmount the image path in source machine.")
				self.SET_RESULT(1)
		else:
			logger.info("The image path dir is not mounted in source machine.")

	def unmount_imagepath_in_targetmachine(self, logger, imagepath, targetmachine_ip):
		''' unmount the image path in the target machine. '''
		cmd = "mount"
		ret, output = self.runcmd(logger, cmd, "showing mount point in target machine", targetmachine_ip)
		if "on %s type nfs" % (imagepath) in output:
			cmd = "umount -f %s" % (imagepath)
			ret, output = self.runcmd(logger, cmd, "unmount the image path in target machine", targetmachine_ip)
			if ret == 0:
				logger.info("Succeeded to unmount the image path in target machine.")
			else:
				logger.error("Failed to unmount the image path in target machine.")
				self.SET_RESULT(1)
		else:
			logger.info("The image path dir is not mounted in target machine.")

	def unmount_rhsmlog_of_targetmachine(self, logger, rhsmlog_for_targetmachine):
		''' unmount the rhsm log of the target machine. '''
		# unmount and remove the dir rhsmlog_for_targetmachine
		if os.path.ismount(rhsmlog_for_targetmachine):
			cmd = "umount -f %s" % (rhsmlog_for_targetmachine)
			ret, output = self.runcmd(logger, cmd, "unmount the rhsm log dir of target machine")
			if ret == 0:
				logger.info("Succeeded to unmount the rhsm log dir of target machine.")
				# remove the dir rhsmlog_for_targetmachine
				os.removedirs(rhsmlog_for_targetmachine)
				logger.info("Removed the dir '%s'." % rhsmlog_for_targetmachine)
			else:
				logger.error("Failed to unmount the rhsm log dir of target machine.")
				self.SET_RESULT(1)

	#========================================================
	# 	4. ESX Functions
	#========================================================
	def esx_add_guest(self, logger, guest_name, destination_ip):
		''' add guest to esx host '''
		cmd = "vim-cmd solo/register /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
		ret, output = self.runcmd_byuser(logger, cmd, "add guest '%s' to ESX '%s'" % (guest_name, destination_ip), destination_ip)
		if ret == 0:
			# need to wait 30 s for add sucess
			time.sleep(60)
			logger.info("Succeeded to add guest '%s' to ESX host" % guest_name)
		else:
			if "AlreadyExists" in output:
				logger.info("Guest '%s' already exist in ESX host" % guest_name)
			else:
				logger.error("Failed to add guest '%s' to ESX host" % guest_name)
				self.SET_RESULT(1)

	def esx_create_dummy_guest(self, logger, guest_name, destination_ip):
		''' create dummy guest in esx '''
		cmd = "vim-cmd vmsvc/createdummyvm %s /vmfs/volumes/datastore*/" % guest_name
		ret, output = self.runcmd_byuser(logger, cmd, "add guest '%s' to ESX '%s'" % (guest_name, destination_ip), destination_ip)
		if ret == 0:
			# need to wait 30 s for add sucess
			time.sleep(60)
			logger.info("Succeeded to add guest '%s' to ESX host" % guest_name)
		else:
			if "AlreadyExists" in output:
				logger.info("Guest '%s' already exist in ESX host" % guest_name)
			else:
				logger.error("Failed to add guest '%s' to ESX host" % guest_name)
				self.SET_RESULT(1)

	def esx_service_restart(self, logger, destination_ip):
		''' restart esx service '''
		cmd = "/etc/init.d/hostd restart; /etc/init.d/vpxa restart"
		ret, output = self.runcmd_byuser(logger, cmd, "restart hostd and vpxa service", destination_ip)
		if ret == 0:
			logger.info("Succeeded to restart hostd and vpxa service")
		else:
			logger.error("Failed to restart hostd and vpxa service")
			self.SET_RESULT(1)
		time.sleep(120)

	def esx_start_guest_first(self, logger, guest_name, destination_ip):
		''' start guest in esx host '''
		cmd = "vim-cmd vmsvc/power.on /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
		ret, output = self.runcmd_byuser(logger, cmd, "start guest '%s' in ESX" % guest_name, destination_ip)
		if ret == 0:
			logger.info("Succeeded to first start guest '%s' in ESX host" % guest_name)
		else:
			logger.info("Failed to first start guest '%s' in ESX host" % guest_name)
		''' Do not check whethre guest can be accessed by ip, since there's an error, need to restart esx service '''
		# self.esx_check_ip_accessable(logger, guest_name, destination_ip, accessable=True)

	def esx_check_system_reboot(self, logger, target_ip):
		time.sleep(120)
		cycle_count = 0
		while True:
			# wait max time 10 minutes
			max_cycle = 60
			cycle_count = cycle_count + 1
			cmd = "ping -c 5 %s" % target_ip
			ret, output = self.runcmd_byuser(logger, cmd, "ping system ip")
			if ret == 0 and "5 received" in output:
				logger.info("Succeeded to ping system ip")
				break
			if cycle_count == max_cycle:
				logger.info("Time out to ping system ip")
				break
			else:
				time.sleep(10)

	def esx_remove_guest(self, logger, guest_name, esx_host, vCenter, vCenter_user, vCenter_pass):
		''' remove guest from esx vCenter '''
		vmware_cmd_ip = ee.vmware_cmd_ip
		cmd = "vmware-cmd -H %s -U %s -P %s --vihost %s -s unregister /vmfs/volumes/datastore*/%s/%s.vmx" % (vCenter, vCenter_user, vCenter_pass, esx_host, guest_name, guest_name)
		ret, output = self.runcmd(logger, cmd, "remove guest '%s' from vCenter" % guest_name, vmware_cmd_ip)
		if ret == 0:
			logger.info("Succeeded to remove guest '%s' from vCenter" % guest_name)
		else:
			logger.error("Failed to remove guest '%s' from vCenter" % guest_name)
			self.SET_RESULT(1)

	def esx_destroy_guest(self, logger, guest_name, esx_host):
		''' destroy guest from '''
		# esx_host_ip = ee.esx_host_ip
		# vmware_cmd_ip = ee.vmware_cmd_ip
		# cmd = "vim-cmd vmsvc/destroy /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
		cmd = "rm -rf /vmfs/volumes/datastore*/%s" % guest_name
		ret, output = self.runcmd_byuser(logger, cmd, "destroy guest '%s' in ESX" % guest_name, esx_host)
		if ret == 0:
			logger.info("Succeeded to destroy guest '%s'" % guest_name)
		else:
			logger.error("Failed to destroy guest '%s'" % guest_name)
			self.SET_RESULT(1)

	def esx_check_host_exist(self, logger, esx_host, vCenter, vCenter_user, vCenter_pass):
		''' check whether esx host exist in vCenter '''
		vmware_cmd_ip = ee.vmware_cmd_ip
		cmd = "vmware-cmd -H %s -U %s -P %s --vihost %s -l" % (vCenter, vCenter_user, vCenter_pass, esx_host)
		ret, output = self.runcmd(logger, cmd, "check whether esx host:%s exist in vCenter" % esx_host, vmware_cmd_ip)
		if "Host not found" in output:
			logger.error("esx host:%s not exist in vCenter" % esx_host)
			return False
		else:
			logger.info("esx host:%s exist in vCenter" % esx_host)
			return True

	def esx_remove_all_guests(self, logger, guest_name, destination_ip):
		return

	def esx_start_guest(self, logger, guest_name):
		''' start guest in esx host '''
		esx_host_ip = ee.esx_host_ip
		cmd = "vim-cmd vmsvc/power.on /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
		ret, output = self.runcmd_byuser(logger, cmd, "start guest '%s' in ESX" % guest_name, esx_host_ip)
		if ret == 0:
			logger.info("Succeeded to start guest '%s' in ESX host" % guest_name)
		else:
			logger.error("Failed to start guest '%s' in ESX host" % guest_name)
			self.SET_RESULT(1)
		''' check whethre guest can be accessed by ip '''
		self.esx_check_ip_accessable(logger, guest_name, esx_host_ip, accessable=True)

	def esx_stop_guest(self, logger, guest_name, destination_ip):
		''' stop guest in esx host '''
		cmd = "vim-cmd vmsvc/power.off /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
		ret, output = self.runcmd_byuser(logger, cmd, "stop guest '%s' in ESX '%s'" % (guest_name, destination_ip), destination_ip)
		if ret == 0:
			logger.info("Succeeded to stop guest '%s' in ESX host" % guest_name)
		else:
			logger.error("Failed to stop guest '%s' in ESX host" % guest_name)
			self.SET_RESULT(1)
		''' check whethre guest can not be accessed by ip '''
		self.esx_check_ip_accessable(logger, guest_name, destination_ip, accessable=False)

	def esx_pause_guest(self, logger, guest_name, destination_ip):
		''' suspend guest in esx host '''
		cmd = "vim-cmd vmsvc/power.suspend /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
		ret, output = self.runcmd_byuser(logger, cmd, "suspend guest '%s' in ESX '%s'" % (guest_name, destination_ip), destination_ip)
		if ret == 0:
			logger.info("Succeeded to suspend guest '%s' in ESX host" % guest_name)
		else:
			logger.error("Failed to suspend guest '%s' in ESX host" % guest_name)
			self.SET_RESULT(1)
		''' check whethre guest can not be accessed by ip '''
		self.esx_check_ip_accessable(logger, guest_name, destination_ip, accessable=False)

	def esx_resume_guest(self, logger, guest_name, destination_ip):
		''' resume guest in esx host '''
		# cmd = "vim-cmd vmsvc/power.suspendResume /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
		cmd = "vim-cmd vmsvc/power.on /vmfs/volumes/datastore*/%s/%s.vmx" % (guest_name, guest_name)
		ret, output = self.runcmd_byuser(logger, cmd, "resume guest '%s' in ESX '%s'" % (guest_name, destination_ip), destination_ip)
		if ret == 0:
			logger.info("Succeeded to resume guest '%s' in ESX host" % guest_name)
		else:
			logger.error("Failed to resume guest '%s' in ESX host" % guest_name)
			self.SET_RESULT(1)
		''' check whethre guest can be accessed by ip '''
		self.esx_check_ip_accessable(logger, guest_name, destination_ip, accessable=True)

	def esx_get_guest_mac(self, logger, guest_name, destination_ip):
		''' get guest mac address in esx host '''
		cmd = "vim-cmd vmsvc/device.getdevices /vmfs/volumes/datastore*/%s/%s.vmx | grep 'macAddress'" % (guest_name, guest_name)
		ret, output = self.runcmd_byuser(logger, cmd, "get guest mac address '%s' in ESX '%s'" % (guest_name, destination_ip), destination_ip)
		macAddress = output.split("=")[1].strip().strip(',').strip('"')
		if ret == 0:
			logger.info("Succeeded to get guest mac address '%s' in ESX host" % guest_name)
		else:
			logger.error("Failed to get guest mac address '%s' in ESX host" % guest_name)
			self.SET_RESULT(1)
		return macAddress
	
	def esx_get_guest_ip(self, logger, guest_name, destination_ip):
		''' get guest ip address in esx host, need vmware-tools installed in guest '''
		cmd = "vim-cmd vmsvc/get.summary /vmfs/volumes/datastore*/%s/%s.vmx | grep 'ipAddress'" % (guest_name, guest_name)
		ret, output = self.runcmd_byuser(logger, cmd, "get guest ip address '%s' in ESX '%s'" % (guest_name, destination_ip), destination_ip, showlogger=False)
		ipAddress = output.split("=")[1].strip().strip(',').strip('"').strip('<').strip('>')
		if ret == 0:
			logger.info("Getting guest ip address '%s' in ESX host" % ipAddress)
		else:
			logger.error("Failed to get guest ip address '%s' in ESX host" % ipAddress)
			self.SET_RESULT(1)
		return ipAddress

	def esx_check_ip_accessable(self, logger, guest_name, destination_ip, accessable):
		cycle_count = 0
		while True:
			# wait max time 10 minutes
			max_cycle = 60
			cycle_count = cycle_count + 1
			if accessable:
				if self.esx_get_guest_ip(logger, guest_name, destination_ip) != "unset":
					break
				if cycle_count == max_cycle:
					logger.info("Time out to esx_check_ip_accessable")
					break
				else:
					time.sleep(10)
			else:
				time.sleep(30)
				if self.esx_get_guest_ip(logger, guest_name, destination_ip) == "unset":
					break
				if cycle_count == max_cycle:
					logger.info("Time out to esx_check_ip_accessable")
					break
				else:
					time.sleep(10)

	def esx_get_guest_uuid(self, logger, guest_name, destination_ip):
		''' get guest uuid in esx host '''
		cmd = "vim-cmd vmsvc/get.summary /vmfs/volumes/datastore*/%s/%s.vmx | grep 'uuid'" % (guest_name, guest_name)
		ret, output = self.runcmd_byuser(logger, cmd, "get guest uuid '%s' in ESX '%s'" % (guest_name, destination_ip), destination_ip)
		uuid = output.split("=")[1].strip().strip(',').strip('"').strip('<').strip('>')
		if ret == 0:
			logger.info("Succeeded to get guest uuid '%s' in ESX host" % guest_name)
		else:
			logger.error("Failed to get guest uuid '%s' in ESX host" % guest_name)
			self.SET_RESULT(1)
		return uuid

	def esx_get_host_uuid(self, logger, destination_ip):
		''' get host uuid in esx host '''
		cmd = "vim-cmd hostsvc/hostsummary | grep 'uuid'"
		ret, output = self.runcmd_byuser(logger, cmd, "get host uuid in ESX '%s'" % destination_ip, destination_ip)
		uuid = output.split("=")[1].strip().strip(',').strip('"').strip('<').strip('>')
		if ret == 0:
			logger.info("Succeeded to get host uuid '%s' in ESX host" % uuid)
		else:
			logger.error("Failed to get host uuid '%s' in ESX host" % uuid)
			self.SET_RESULT(1)
		return uuid

	def esx_check_uuid(self, logger, guestname, destination_ip, guestuuid="Default", uuidexists=True, rhsmlogpath='/var/log/rhsm'):
		''' check if the guest uuid is correctly monitored by virt-who '''
		if guestname != "" and guestuuid == "Default":
			guestuuid = self.esx_get_guest_uuid(logger, guestname, destination_ip)
		rhsmlogfile = os.path.join(rhsmlogpath, "rhsm.log")
		self.vw_restart_virtwho(logger)
		self.vw_restart_virtwho(logger)
		cmd = "tail -1 %s " % rhsmlogfile
		ret, output = self.runcmd(logger, cmd, "check output in rhsm.log")
		if ret == 0:
			''' get guest uuid.list from rhsm.log '''
			if "Sending list of uuids: " in output:
				log_uuid_list = output.split('Sending list of uuids: ')[1]
				logger.info("Succeeded to get guest uuid.list from rhsm.log.")
			elif "Sending update to updateConsumer: " in output:
				log_uuid_list = output.split('Sending update to updateConsumer: ')[1]
				logger.info("Succeeded to get guest uuid.list from rhsm.log.")
			elif "Sending update in hosts-to-guests mapping: " in output:
				log_uuid_list = output.split('Sending update in hosts-to-guests mapping: ')[1].split(":")[1].strip("}").strip()
				logger.info("Succeeded to get guest uuid.list from rhsm.log.")
			else:
				logger.error("Failed to get guest %s uuid.list from rhsm.log" % guestname)
				self.SET_RESULT(1)
			# check guest uuid in log_uuid_list
			if uuidexists:
				if guestname == "":
					return len(log_uuid_list) == 0
				else:
					return guestuuid in log_uuid_list
			else:
				if guestname == "":
					return not len(log_uuid_list) == 0
				else:
					return not guestuuid in log_uuid_list
		else:
			logger.error("Failed to get uuids in rhsm.log")
			self.SET_RESULT(1)

	def esx_check_uuid_exist_in_rhsm_log(self, logger, uuid, destination_ip=""):
		''' esx_check_uuid_exist_in_rhsm_log '''
		self.vw_restart_virtwho(logger)
		self.vw_restart_virtwho(logger)
		time.sleep(10)
		cmd = "tail -1 /var/log/rhsm/rhsm.log"
		ret, output = self.runcmd(logger, cmd, "check output in rhsm.log")
		if ret == 0:
			''' get guest uuid.list from rhsm.log '''
			if "Sending list of uuids: " in output:
				log_uuid_list = output.split('Sending list of uuids: ')[1]
				logger.info("Succeeded to get guest uuid.list from rhsm.log.")
			elif "Sending update to updateConsumer: " in output:
				log_uuid_list = output.split('Sending update to updateConsumer: ')[1]
				logger.info("Succeeded to get guest uuid.list from rhsm.log.")
			elif "Sending update in hosts-to-guests mapping: " in output:
				log_uuid_list = output.split('Sending update in hosts-to-guests mapping: ')[1].split(":")[1].strip("}").strip()
				logger.info("Succeeded to get guest uuid.list from rhsm.log.")
			else:
				logger.error("Failed to get guest uuid.list from rhsm.log")
				self.SET_RESULT(1)
			# check guest uuid in log_uuid_list
			return uuid in log_uuid_list
		else:
			logger.error("Failed to get uuids in rhsm.log")
			self.SET_RESULT(1)

	def get_uuid_list_in_rhsm_log(self, logger, destination_ip=""):
		''' esx_check_uuid_exist_in_rhsm_log '''
		self.vw_restart_virtwho(logger)
		time.sleep(20)
		cmd = "tail -1 /var/log/rhsm/rhsm.log"
		ret, output = self.runcmd(logger, cmd, "check output in rhsm.log")
		if ret == 0:
			''' get guest uuid.list from rhsm.log '''
			if "Sending list of uuids: " in output:
				log_uuid_list = output.split('Sending list of uuids: ')[1]
				logger.info("Succeeded to get guest uuid.list from rhsm.log.")
			elif "Sending update to updateConsumer: " in output:
				log_uuid_list = output.split('Sending update to updateConsumer: ')[1]
				logger.info("Succeeded to get guest uuid.list from rhsm.log.")
			elif "Sending update in hosts-to-guests mapping: " in output:
				log_uuid_list = output.split('Sending update in hosts-to-guests mapping: ')[1].split(":")[1].strip("}").strip()
				logger.info("Succeeded to get guest uuid.list from rhsm.log.")
			else:
				logger.error("Failed to get guest uuid.list from rhsm.log")
				self.SET_RESULT(1)
			return log_uuid_list
		else:
			logger.error("Failed to get uuid list in rhsm.log")
			self.SET_RESULT(1)

	def esx_check_host_in_samserv(self, logger, esx_uuid, destination_ip):
		''' check esx host exist in sam server '''
		cmd = "headpin -u admin -p admin system list --org=ACME_Corporation --environment=Library"
		ret, output = self.runcmd(logger, cmd, "check esx host exist in sam server", destination_ip)
		if ret == 0 and esx_uuid in output:
		# if ret == 0 and output.find(esx_uuid) >= 0:
			logger.info("Succeeded to check esx host %s exist in sam server" % esx_uuid)
		else:
			logger.error("Failed to check esx host %s exist in sam server" % esx_uuid)
			self.SET_RESULT(1)

	def esx_remove_host_in_samserv(self, logger, esx_uuid, destination_ip):
		''' remove esx host in sam server '''
		cmd = "headpin -u admin -p admin system unregister --name=%s --org=ACME_Corporation" % esx_uuid
		ret, output = self.runcmd(logger, cmd, "remove esx host in sam server", destination_ip)
		if ret == 0 and esx_uuid in output:
			logger.info("Succeeded to remove esx host %s in sam server" % esx_uuid)
		else:
			logger.error("Failed to remove esx host %s in sam server" % esx_uuid)
			self.SET_RESULT(1)

	def esx_remove_deletion_record_in_samserv(self, logger, esx_uuid, destination_ip):
		''' remove deletion record in sam server '''
		cmd = "headpin -u admin -p admin system remove_deletion --uuid=%s" % esx_uuid
		ret, output = self.runcmd(logger, cmd, "remove deletion record in sam server", destination_ip)
		if ret == 0 and esx_uuid in output:
			logger.info("Succeeded to remove deletion record %s in sam server" % esx_uuid)
		else:
			logger.error("Failed to remove deletion record %s in sam server" % esx_uuid)
			self.SET_RESULT(1)

	def esx_subscribe_host_in_samserv(self, logger, esx_uuid, poolid, destination_ip):
		''' subscribe host in sam server '''
		cmd = "headpin -u admin -p admin system subscribe --name=%s --org=ACME_Corporation --pool=%s " % (esx_uuid, poolid)
		ret, output = self.runcmd(logger, cmd, "subscribe host in sam server", destination_ip)
		if ret == 0 and esx_uuid in output:
			logger.info("Succeeded to subscribe host %s in sam server" % esx_uuid)
		else:
			logger.error("Failed to subscribe host %s in sam server" % esx_uuid)
			self.SET_RESULT(1)

	def esx_unsubscribe_all_host_in_samserv(self, logger, esx_uuid, destination_ip):
		''' unsubscribe host in sam server '''
		cmd = "headpin -u admin -p admin system unsubscribe --name=%s --org=ACME_Corporation --all" % esx_uuid
		ret, output = self.runcmd(logger, cmd, "unsubscribe host in sam server", destination_ip)
		if ret == 0 and esx_uuid in output:
			logger.info("Succeeded to unsubscribe host %s in sam server" % esx_uuid)
		else:
			logger.error("Failed to unsubscribe host %s in sam server" % esx_uuid)
			self.SET_RESULT(1)

	def get_poolid_by_SKU(self, logger, sku, targetmachine_ip=""):
		''' get_poolid_by_SKU '''
		availpoollist = self.sub_listavailpools(logger, sku, targetmachine_ip)
		if availpoollist != None:
			for index in range(0, len(availpoollist)):
				if("SKU" in availpoollist[index] and availpoollist[index]["SKU"] == sku):
					rindex = index
					break
				elif("ProductId" in availpoollist[index] and availpoollist[index]["ProductId"] == sku):
					rindex = index
					break
			if "PoolID" in availpoollist[index]:
				poolid = availpoollist[rindex]["PoolID"]
			else:
				poolid = availpoollist[rindex]["PoolId"]
			return poolid
		else:
			logger.error("Failed to subscribe to the pool of the product: %s - due to failed to list available pools." % sku)
			self.SET_RESULT(1)

	#========================================================
	# 	5. Rhevm Functions
	#========================================================
	def add_rhevm_server_to_host(self, logger, rhevmmachine_name, rhevmmachine_ip, targetmachine_ip=""):
		''' Add rhevm hostname and hostip to /etc/hosts '''
		cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (rhevmmachine_ip, rhevmmachine_ip, rhevmmachine_name)
		ret, output = self.runcmd(logger, cmd, "add rhevm name and ip to /etc/hosts", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to add rhevm hostip %s and rhevm hostname %s %s." % (rhevmmachine_ip, rhevmmachine_name, self.get_HG_info(targetmachine_ip)))
		else:
			logger.error("Failed to add rhevm hostip %s and rhevm hostname %s %s" % (rhevmmachine_ip, rhevmmachine_name, self.get_HG_info(targetmachine_ip)))
			self.SET_RESULT(1)

	def configure_host_bridge(self, logger, rhevmmachine_name, rhevmmachine_ip, targetmachine_ip=""):
		eth0_addr = '/etc/sysconfig/network-scripts/ifcfg-eth0'
		br0_addr = '/etc/sysconfig/network-scripts/ifcfg-br0'
		cmd = "ifconfig rhevm"
		ret, output = self.runcmd(logger, cmd, "Check bridge rhevm exist", targetmachine_ip)
		''' configure the host bridge. '''
		if ret != 0 and rhevmmachine_name != None and rhevmmachine_ip != None :
			# set the eth0's bridge to rhevm
			cmd = "sed -i '/^BRIDGE/d' %s ; echo 'BRIDGE=rhevm' >> %s" % (eth0_addr, eth0_addr)
			ret, output = self.runcmd(logger, cmd, "configure eth0 bridge name to rhevm", targetmachine_ip)
			if ret == 0:
				logger.info("Succeeded to configure eth0 bridge name to rhevm")
			else:
				logger.error("Failed to configure eth0 bridge name to rhevm")
				self.SET_RESULT(1)
			cmd = "sed -i '/^DEVICE/d' %s ; echo 'DEVICE=rhevm' >> %s" % (br0_addr, br0_addr)
			ret, output = self.runcmd(logger, cmd, "configure br0 drive name to rhevm", targetmachine_ip)
			if ret == 0:
				logger.info("Succeeded to configure br0 drive name to rhevm")
			else:
				logger.error("Failed to configure br0 drive name to rhevm")
				self.SET_RESULT(1)
			cmd = "init 6"
			ret, output = self.runcmd(logger, cmd, "reboot system", targetmachine_ip)
			if ret == 0:
				logger.info("Start to reboot system %s, please wait for a moment!" % targetmachine_ip)
			else:
				logger.error("Failed to reboot system %s, please wait for a moment!" % targetmachine_ip)
				self.SET_RESULT(1)
			self.ping_host(logger, targetmachine_ip)
			cmd = "ifconfig rhevm"
			ret, output = self.runcmd(logger, cmd, "Check bridge rhevm exist", targetmachine_ip)
			if ret == 0 :
				logger.info("Succesfully to configured bridge rhevm on %s" % targetmachine_ip)
			else:
				logger.error("Failed to configured bridge rhevm on %s" % targetmachine_ip)
				self.SET_RESULT(1)

	def ping_host(self, logger, ip, timeout=600):
		"""Ping some host,return True on success or False on Failure,timeout should be greater or equal to 10"""
		time.sleep(10)
		cmd = "ping -c 3 " + str(ip)
		while True:
			if(timeout > 0):
				time.sleep(10)
				timeout -= 10
				(ret, out) = commands.getstatusoutput(cmd)
				if ret == 0:
					logger.info("ping successfully")
					time.sleep(30)
					break
				logger.info("left %s s to reboot %s" % (timeout, ip))
			else:
				logger.error("ping time out")
				self.SET_RESULT(1)

	def get_rhevm_repo_file(self, logger, targetmachine_ip=""):
		''' wget rhevm repo file and add to rhel host '''
		cmd = "wget -P /etc/yum.repos.d/ http://10.66.100.116/projects/sam-virtwho/rhevm-6.5.repo"
		ret, output = self.runcmd(logger, cmd, "wget rhevm repo file and add to rhel host", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to wget rhevm repo file and add to rhel host")
		else:
			logger.error("Failed to wget rhevm repo file and add to rhel host")
			self.SET_RESULT(1)

	def install_host_vdsm(self, logger, rhevmmachine_name, rhevmmachine_ip, targetmachine_ip=""):
		'''install VDSM'''
		if rhevmmachine_name != None and rhevmmachine_ip != None:
			cmd = "rpm -q vdsm"
			ret, output = self.runcmd(logger, cmd, "check whether vdsm exist", targetmachine_ip)      
			if ret == 0:
				logger.info("vdsm has already exist, needn't to install it.")
			else:
				cmd = "yum install vdsm -y"
				ret, output = self.runcmd(logger, cmd, "install vdsm", targetmachine_ip)
				if ret == 0 and "Complete!" in output:
					logger.info("Succeeded to install vdsm.")
				elif ret == 0 and "already installed" in output:
					logger.info("vdsm has been installed.")
				else:
					logger.error("Failed to install vdsm")
					self.SET_RESULT(1)

	def install_virtV2V(self, logger, rhevmmachine_name, rhevmmachine_ip, targetmachine_ip=""):
		'''install virt-V2V'''
		if rhevmmachine_name != None and rhevmmachine_ip != None:
			cmd = "rpm -q virt-v2v"
			ret, output = self.runcmd(logger, cmd, "check whether virt-V2V exist", targetmachine_ip)
			if ret == 0:
				logger.info("virt-V2V has already exist, needn't to install it.")
			else:
				logger.info("virt-V2V hasn't been installed.")
				cmd = "yum install virt-v2v -y"
				ret, output = self.runcmd(logger, cmd, "install vdsm", targetmachine_ip)
				if ret == 0 and "Complete!" in output:
					logger.info("Succeeded to install virt-V2V.")
				else:
					logger.error("Failed to install virt-V2V")
					self.SET_RESULT(1)

	def rhevm_update_vw_configure(self, logger, rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password, background=1, debug=1, targetmachine_ip=""):
		''' update virt-who configure file /etc/sysconfig/virt-who. '''
		cmd = "sed -i -e 's/#VIRTWHO_INTERVAL=.*/VIRTWHO_INTERVAL=5/g' -e 's/VIRTWHO_BACKGROUND=.*/VIRTWHO_BACKGROUND=%s/g' -e 's/VIRTWHO_DEBUG=.*/VIRTWHO_DEBUG=%s/g' -e 's/#VIRTWHO_RHEVM=.*/VIRTWHO_RHEVM=1/g' -e 's/#VIRTWHO_RHEVM_OWNER=.*/VIRTWHO_RHEVM_OWNER=%s/g' -e 's/#VIRTWHO_RHEVM_ENV=.*/VIRTWHO_RHEVM_ENV=%s/g' -e 's/#VIRTWHO_RHEVM_SERVER=.*/VIRTWHO_RHEVM_SERVER=%s/g' -e 's/#VIRTWHO_RHEVM_USERNAME=.*/VIRTWHO_RHEVM_USERNAME=%s/g' -e 's/#VIRTWHO_RHEVM_PASSWORD=.*/VIRTWHO_RHEVM_PASSWORD=%s/g' /etc/sysconfig/virt-who" % (background, debug, rhevm_owner, rhevm_env, rhevm_server, rhevm_username, rhevm_password)
		ret, output = self.runcmd(logger, cmd, "updating virt-who configure file", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to update virt-who configure file.")
		else:
			logger.error("Failed to update virt-who configure file.")
			self.SET_RESULT(1)

	# Get the machine's hostname
	def get_hostname(self, logger, targetmachine_ip=""):
		cmd = "hostname"
		ret, output = self.runcmd(logger, cmd, "geting the machine's hostname", targetmachine_ip)
		if ret == 0:
			hostname = output.strip(' \r\n').strip('\r\n') 
			logger.info("Succeeded to get the machine's hostname %s." % hostname) 
			return hostname
		else:
			logger.error("Failed to get the machine's hostname.")
			self.SET_RESULT(1)

	def rhevm_add_dns_to_host(self, logger, DNSserver_ip, targetmachine_ip=""):
		''' add dns server to /etc/resolv.conf. '''
		cmd = "sed -i '/%s/d' /etc/resolv.conf; sed -i '/search/a nameserver %s' /etc/resolv.conf" % (DNSserver_ip, DNSserver_ip)
		ret, output = self.runcmd(logger, cmd, "add_dns_to_host in /etc/resolv.conf.", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to add_dns_to_host in /etc/resolve.conf.")
		else:
			logger.error("Failed to add_dns_to_host in /etc/resolve.conf.")
			self.SET_RESULT(1)

	def add_dns_to_host(self, logger, DNSserver_ip, targetmachine_ip=""):
		''' add dns server to /etc/resolv.conf. '''
		cmd = "sed -i '/%s/d' /etc/resolv.conf; sed -i '/search/a nameserver %s\nnameserver 10.16.101.41\nnameserver 10.11.5.19' /etc/resolv.conf" % (DNSserver_ip, DNSserver_ip)
		ret, output = self.runcmd(logger, cmd, "add_dns_to_host in /etc/resolv.conf.", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to add_dns_to_host in /etc/resolve.conf.")
		else:
			logger.error("Failed to add_dns_to_host in /etc/resolve.conf.")
			self.SET_RESULT(1)
		# make /etc/resolv.conf can not be changed 
		cmd = "chattr +i /etc/resolv.conf"
		ret, output = self.runcmd(logger, cmd, "Fix /etc/resolv.conf.", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to fix /etc/resolve.conf.")
		else:
			logger.error("Failed to fix /etc/resolve.conf.")
			self.SET_RESULT(1)

	# Convert the ip address's last two bits
	def get_conv_ip(self, logger, sourceip, targetmachine_ip=""):
		convtip = sourceip.split(".")
		logger.info("Succeeded to get converted ip address %s" % convtip)
		return convtip[3] + "." + convtip[2]

	# Remove hostname's '.redhat.com'
	def get_conv_name(self, logger, sourcename, targetmachine_ip=""):
		convtname = sourcename[0:sourcename.rfind('.redhat.com')] 
		logger.info("Succeeded to get convname %s" % convtname)
		return convtname

	# configure dns server
	def config_dnsserver(self, logger, host_ip, host_name, targetmachine_ip):
		''' configure dns server '''
		dirct_addr = '/var/named/named.66.10'
		revert_addr = '/var/named/named.redhat.com'
		conv_host_ip = self.get_conv_ip(logger, host_ip)
		conv_host_name = self.get_conv_name(logger, host_name)
		cmd = "sed -i '/%s/d' %s; sed -i '$ a\%s\tIN\tPTR\t%s.' %s" % (host_name, dirct_addr, conv_host_ip, host_name, dirct_addr)
		ret, output = self.runcmd_indns(logger, cmd, "Add host %s ip address to named.66.10" % host_ip, targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to add host's ip %s to DNS server." % host_ip)
		else:
			logger.error("Failed to add host's ip %s to DNS server." % host_ip)
			self.SET_RESULT(1) 
		cmd = "sed -i '/%s/d' %s; sed -i '$ a\%s\tIN\tA\t%s' %s" % (conv_host_name, revert_addr, conv_host_name, host_ip, revert_addr) 
		ret, output = self.runcmd_indns(logger, cmd, "Add host name %s to named.redhat.com" % host_name, targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to add host's name %s to DNS server." % host_name)
		else:
			logger.error("Failed to add host's name %s to DNS server." % host_name)
			self.SET_RESULT(1)
		# restart dns service
		cmd = "service named restart"
		ret, output = self.runcmd_indns(logger, cmd, "service named restart", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to restart dns service.")
		else:
			logger.error("Failed to restart dns service.")
			self.SET_RESULT(1)

	# configure dns server
	def config_yum(self, logger, proxy_ip, targetmachine_ip):
		''' configure yum '''
		cmd = "sed -i '/%s/d' /etc/yum.conf; sed -i '/search/a %s' /etc/yum.conf" % (proxy_ip, proxy_ip)
		ret, output = self.runcmd(logger, cmd, "add proxy to /etc/yum.conf.", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to add proxy to /etc/yum.conf.")
		else:
			logger.error("Failed to add proxy to /etc/yum.conf.")
			self.SET_RESULT(1)

	# configure rhsm.conf to candlepin server
	def conf_rhsm_candlepin(self, logger, targetmachine_ip):
		''' configure candlepin '''
		cmd = "sed -i -e 's/^hostname =.*/hostname = subscription.rhn.redhat.com/g' -e 's/baseurl=.*/baseurl=https:\/\/cdn.redhat.com/g' /etc/rhsm/rhsm.conf"
		ret, output = self.runcmd(logger, cmd, "Configure candlepin server.", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to configure candlepin server.")
		else:
			logger.error("Failed to Configure candlepin server.")
			self.SET_RESULT(1)

	# configure rhsm.conf to sam server
	def conf_rhsm_sam(self, logger, targetmachine_ip):
		''' configure candlepin '''
		cmd = "sed -i -e 's/hostname =.*/hostname = samserv.redhat.com/g' -e 's/baseurl=.*/baseurl=https:\/\/samserv.redhat.com:8088/g' /etc/rhsm/rhsm.conf"
		ret, output = self.runcmd(logger, cmd, "Configure SAM server.", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to configure SAM server.")
		else:
			logger.error("Failed to Configure SAM server.")
			self.SET_RESULT(1)

	# Configure NFS server
	def config_nfsserver(self, logger, exportdir, targetmachine_ip=""):
		cmd = "ll %s" % (exportdir)
		ret, output = self.runcmd(logger, cmd, "check images path in the NFS Server", targetmachine_ip)
		if ret == 0 and output is not "":
			cmd = "rm -rf %s/*" % (exportdir)
			ret, output = self.runcmd(logger, cmd, "It has content in the exportdir, need to delete", targetmachine_ip)
			if ret == 0:
				logger.info("Succeeded to delete content in the exportdir.")
			else:
				logger.error("Failed to delete content in the exportdir.")
				self.SET_RESULT(1)            
		cmd = "mkdir -p %s" % (exportdir)
		ret, output = self.runcmd(logger, cmd, "create image path in the NFS Server", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to create imagepath in the source machine.")
		else:
			logger.error("Failed to create imagepath in the source machine.")
			self.SET_RESULT(1)
		''' export a dir as nfs '''
		cmd = "sed -i '/%s/d' /etc/exports; echo '%s *(rw,no_root_squash)' >> /etc/exports" % (exportdir.replace('/', '\/'), exportdir)
		# logger.info(cmd)
		ret, output = self.runcmd(logger, cmd, "set exporting destination dir", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to add '%s *(rw,no_root_squash)' to /etc/exports file." % exportdir)
		else:
			logger.error("Failed to add '%s *(rw,no_root_squash)' to /etc/exports file." % exportdir)
			self.SET_RESULT(1)
		cmd = "service nfs restart; sleep 10"
		ret, output = self.runcmd(logger, cmd, "restarting nfs service", targetmachine_ip)
		if ret == 0 :
			logger.info("Succeeded to restart service nfs.")
		else:
			logger.error("Failed to restart service nfs.")
			self.SET_RESULT(1)
		cmd = "rpc.mountd"
		ret, output = self.runcmd(logger, cmd, "rpc.mountd", targetmachine_ip)
		cmd = "showmount -e 127.0.0.1"
		ret, output = self.runcmd(logger, cmd, "showmount", targetmachine_ip)
		if ret == 0 and (exportdir in output):
			logger.info("Succeeded to export dir '%s' as nfs." % exportdir)
		else:
			logger.error("Failed to export dir '%s' as nfs." % exportdir)
			self.SET_RESULT(1)

	# Configure rhevm-hell, auto connect
	def config_rhevm_shell(self, logger, rhevmserv_ip):
		cmd = "echo -e '[ovirt-shell]\nusername = admin@internal\nca_file = /etc/pki/ovirt-engine/ca.pem\nurl = https://%s:443/api\ninsecure = False\nno_paging = False\nfilter = False\ntimeout = -1\npassword = redhat' > /root/.rhevmshellrc" % rhevmserv_ip
		ret, output = self.runcmd(logger, cmd, "config_rhevm_shell in /root/.rhevmshellrc", rhevmserv_ip)
		if ret == 0:
			logger.info("Succeeded to config_rhevm_shell in /root/.rhevmshellrc.")
		else:
			logger.error("Failed to config_rhevm_shell in /root/.rhevmshellrc.")
			self.SET_RESULT(1)

	# Enter rhevm-shell mode
	def enter_rhevm_shell(self, logger, targetmachine_ip):
		cmd = "rhevm-shell -c" 
		ret, output = self.runcmd(logger, cmd, "connect to rhevm-shell", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to connect to rhevm-shell.")
		else:
			logger.error("Failed to connect to rhevm-shell.")
			self.SET_RESULT(1)

	# Add host to rhevm
	def rhevm_add_host(self, logger, rhevm_host_name, rhevm_host_ip, targetmachine_ip):
		cmd = "add host --name \"%s\" --address \"%s\" --root_password redhat; exit" % (rhevm_host_name, rhevm_host_ip)
		ret, output = self.runcmd_rhevm(logger, cmd, "add host to rhevm.", targetmachine_ip)
		if ret == 0:
			runtime = 0
			while True:
				cmd = "list hosts --show-all; exit"
				ret, output = self.runcmd_rhevm(logger, cmd, "list hosts in rhevm.", targetmachine_ip)
				runtime = runtime + 1
				if ret == 0 and rhevm_host_name in output:
					logger.info("Succeeded to list host %s." % rhevm_host_name)
					status = self.get_key_rhevm(logger, output, "status-state", "name", rhevm_host_name, targetmachine_ip)
					if "up" in status:
						logger.info("Succeeded to add new host %s to rhevm" % rhevm_host_name)
						break
					else :
						logger.info("vm %s status-state is %s" % (rhevm_host_name, status))
				time.sleep(10)
				if runtime > 120:
					logger.error("%s status has problem,status is %s." % (rhevm_host_name, status))
					self.SET_RESULT(1)

	# Get host_id in the rhevm
	def get_hostid_rhevm(self, logger, hostname, targetmachine_ip=""):
		''' Get the hostid. '''
		pool_dict = {}
		self.enter_rhevm_shell(logger, targetmachine_ip)
		cmd = "list hosts"
		output = self.runcmd_rhevmprocess(logger, cmd, "list all hosts in rhevm")
		if output is not "":
			datalines = output.splitlines()
			for line in datalines:
				line = line.strip()
				if line.find("id") == 0:
					resultid = line[(line.find(':') + 1):].strip()
				elif line.find("name") == 0:
					resultname = line[(line.find(':') + 1):].strip()
					pool_dict[resultname] = resultid
			if hostname in pool_dict :
				logger.info("Succeeded to get the %s's hostid." % hostname)
				hostid = pool_dict[hostname]
				return hostid
			else:
				logger.error("Failed to get the %s's hostid." % hostname)
				self.SET_RESULT(1)
		else:
			logger.error("Failed to list hosts on rhevm.")
			self.SET_RESULT(1)

	# parse rhevm-shell result to dict
	def get_key_rhevm(self, logger, output, non_key_value, key_value, find_value, targetmachine_ip=""):
		pool_dict = {}
		if output is not "":
			datalines = output.splitlines()
			values1 = False
			values2 = False
			ERROR_VALUE = "-1"
			for line in datalines:
				line = line.strip()
				if line.find(non_key_value) == 0:
					result_values1 = line[(line.find(':') + 1):].strip()
					logger.info("Succeeded to find the non_key_value %s's result_values1 %s" % (non_key_value, result_values1))
					values1 = True
				elif line.find(key_value) == 0:
					result_values2 = line[(line.find(':') + 1):].strip()
					logger.info("Succeeded to find the key_value %s's result_values2 %s" % (key_value, result_values2))
					values2 = True
				elif (line == "") and (values2 == True) and (values1 == False):
					pool_dict[result_values2] = ERROR_VALUE
					values2 = False
				if (values1 == True) and (values2 == True):
					pool_dict[result_values2] = result_values1
					values1 = False
					values2 = False
			if find_value in pool_dict:
				findout_value = pool_dict[find_value]
				if findout_value == ERROR_VALUE:
					logger.info("Failed to get the %s's %s, no value" % (find_value, non_key_value))
					return ERROR_VALUE
				else:
					logger.info("Succeeded to get the %s's %s." % (find_value, non_key_value))
					return findout_value
			else:
				logger.error("Failed to get the %s's %s" % (find_value, non_key_value))
				self.SET_RESULT(1)
		else:
			logger.error("Failed to run rhevm-shell cmd.")
			self.SET_RESULT(1)

	# parse rhevm-result to dict
	def rhevm_info_dict(self, logger, output, targetmachine_ip=""):
		rhevm_info_dict = {}
		if output is not "":
			datalines = output.splitlines()
			for line in datalines:
				if ":" in line:
					key = line.strip().split(":")[0].strip()
					value = line.strip().split(":")[1].strip()
					print key + "==" + value
					rhevm_info_dict[key] = value
			return rhevm_info_dict
		else:
			logger.error("Failed to get output in rhevm-result file.")
			self.SET_RESULT(1)

	# check rhevm-shell running in rhevm server finished
	def check_rhevm_shell_finished(self, logger, rhevm_ip=""):
		timout = 0
		while True:
			timout = timout + 1
			(ret, output) = utils().remote_exec_pexpect(rhevm_ip, "root", "redhat", "cat /tmp/rhevm_control")
			if ret == 0 and "0" in output:
				logger.info("rhevm-shell command running in rhevm server has finished.")
				time.sleep(10)
				return True
			elif timout > 60:
				logger.error("Time out, running rhevm-shell command in server failed.")
				break
			else:
				logger.info("sleep 10 in check_rhevm_shell_finished.")
				time.sleep(10)

	# wait for a while until expect status shown in /tmp/rhevm-result file
	def wait_for_status(self, logger, cmd, status_key, status_value, targetmachine_ip, timeout=600):
		timout = 0
		while True:
			timout = timout + 1
			# cmd = "list hosts --show-all; exit"
			ret, output = self.runcmd_rhevm(logger, cmd, "list hosts info in rhevm.", targetmachine_ip)
			rhevm_info = self.rhevm_info_dict(logger, output)
			if status_value == "NotExist":
				if not status_key in rhevm_info.keys():
					logger.info("Succeded to check %s not exist." % status_key)
					return True
			elif status_key in rhevm_info.keys() and rhevm_info[status_key] == status_value:
				logger.info("Succeeded to get %s value %s in rhevm." % (status_key, status_value))
				return True
			elif status_key in rhevm_info.keys() and rhevm_info[status_key] != status_value:
				logger.info("Succeeded to remove %s" % status_value)
				return True
			elif timout > 60:
				logger.error("Time out, running rhevm-shell command in server failed.")
				return False
			else:
				logger.info("sleep 10 in wait_for_status.")
				time.sleep(10)

	# Add storagedomain in rhevm
	def add_storagedomain_to_rhevm(self, logger, storage_name, hostname, domaintype, storage_format, NFS_server, export_dir, rhevm_host_ip): 
		# clean storage nfs folder first
		cmd = "rm -rf %s/*" % export_dir
		ret, output = self.runcmd(logger, cmd, "clean storage nfs folder", NFS_server)
		if ret == 0:
			logger.info("Succeeded to clean storage nfs folder: %s" % export_dir)
		else:
			logger.error("Failed to clean storage nfs folder: %s" % export_dir)
			self.SET_RESULT(1)
		cmd = "add storagedomain --name \"%s\" --host-name \"%s\"  --type \"%s\" --storage-type \"nfs\" --storage_format \"%s\" --storage-address \"%s\" --storage-path \"%s\" --datacenter \"Default\"" % (storage_name, hostname, domaintype, storage_format, NFS_server, export_dir)
		ret, output = self.runcmd_rhevm(logger, cmd, "Add storagedomain in rhevm.", rhevm_host_ip)
		if self.wait_for_status(logger, "list storagedomains --show-all; exit", "status-state", "unattached", rhevm_host_ip):
			logger.info("Succeeded to add storagedomains %s in rhevm." % storage_name)
		else:
			logger.error("Failed to add storagedomains %s in rhevm." % storage_name)
			self.SET_RESULT(1)
		cmd = "add storagedomain --name \"%s\" --host-name \"%s\"  --type \"%s\" --storage-type \"nfs\" --storage_format \"%s\" --storage-address \"%s\" --storage-path \"%s\" --datacenter-identifier \"Default\"" % (storage_name, hostname, domaintype, storage_format, NFS_server, export_dir)
		ret, output = self.runcmd_rhevm(logger, cmd, "Add storagedomain in rhevm.", rhevm_host_ip)
		if self.wait_for_status(logger, "list storagedomains --show-all; exit", "status-state", "NotExist", rhevm_host_ip):
			logger.info("Succeeded to maintenance storagedomains %s in rhevm." % storage_name)
		else:
			logger.error("Failed to maintenance storagedomains %s in rhevm." % storage_name)
			self.SET_RESULT(1)

	# activate storagedomain in rhevm
	def activate_storagedomain(self, logger, storage_name, rhevm_host_ip): 
		cmd = "action storagedomain \"%s\" activate --datacenter-identifier \"Default\"" % (storage_name)
		ret, output = self.runcmd_rhevm(logger, cmd, "activate storagedomain in rhevm.", rhevm_host_ip)
		if self.wait_for_status(logger, "list storagedomains --show-all; exit", "status-state", "NotExist", rhevm_host_ip):
			logger.info("Succeeded to activate storagedomains %s in rhevm." % storage_name)
		else:
			logger.error("Failed to activate storagedomains %s in rhevm." % storage_name)
			self.SET_RESULT(1)

	# convert_guest_to_nfs with v2v tool
	def convert_guest_to_nfs(self, logger, NFS_server, NFS_export_dir, vm_hostname):
		cmd = "virt-v2v -i libvirt -ic qemu:///system -o rhev -os %s:%s --network rhevm %s" % (NFS_server, NFS_export_dir, vm_hostname)
		ret, output = self.runcmd(logger, cmd, "convert_guest_to_nfs with v2v tool")
		if ret == 0:
			logger.info("Succeeded to convert_guest_to_nfs with v2v tool")
		else:
			logger.error("Failed to convert_guest_to_nfs with v2v tool")
			self.SET_RESULT(1)
		# convert the second guest
		cmd = "virt-v2v -i libvirt -ic qemu:///system -o rhev -os %s:%s --network rhevm %s -on \"Sec_%s\"" % (NFS_server, NFS_export_dir, vm_hostname, vm_hostname)
		ret, output = self.runcmd(logger, cmd, "convert_guest_to_nfs with v2v tool")
		if ret == 0:
			logger.info("Succeeded to convert the second guest to nfs with v2v tool")
		else:
			logger.error("Failed to convert the second guest to nfs with v2v tool")
			self.SET_RESULT(1)

	# create_storage_pool
	def create_storage_pool(self, logger):
		''' wget autotest_pool.xml '''
		cmd = "wget -P /tmp/ http://10.66.100.116/projects/sam-virtwho/autotest_pool.xml"
		ret, output = self.runcmd(logger, cmd, "wget rhevm repo file and add to rhel host")
		if ret == 0:
			logger.info("Succeeded to wget autotest_pool.xml")
		else:
			logger.error("Failed to wget autotest_pool.xml")
			self.SET_RESULT(1)
		# check whether pool exist, if yes, destroy it
		cmd = "virsh pool-list"
		ret, output = self.runcmd(logger, cmd, "check whether autotest_pool exist")
		if ret == 0 and "autotest_pool" in output:
			logger.info("autotest_pool exist.")
			cmd = "virsh pool-destroy autotest_pool"
			ret, output = self.runcmd(logger, cmd, "destroy autotest_pool")
			if ret == 0 and "autotest_pool destroyed" in output:
				logger.info("Succeeded to destroy autotest_pool")
			else:
				logger.error("Failed to destroy autotest_pool")
				self.SET_RESULT(1)

		cmd = "virsh pool-create /tmp/autotest_pool.xml"
		ret, output = self.runcmd(logger, cmd, "import vm to rhevm.")
		if ret == 0 and "autotest_pool created" in output:
			logger.info("Succeeded to create autotest_pool.")
		else:
			logger.error("Failed to create autotest_pool.")
			self.SET_RESULT(1)

	# import guest to rhevm
	def import_vm_to_rhevm(self, logger, guest_name, nfs_dir_for_storage, nfs_dir_for_export, rhevm_host_ip):
		# action vm "6.4_Server_x86_64" import_vm --storagedomain-identifier export_storage  --cluster-name Default --storage_domain-name data_storage
		cmd = "action vm \"%s\" import_vm --storagedomain-identifier %s --cluster-name Default --storage_domain-name %s" % (guest_name, nfs_dir_for_export, nfs_dir_for_storage)
		ret, output = self.runcmd_rhevm(logger, cmd, "import guest %s in rhevm." % guest_name, rhevm_host_ip)
		if ret == 0:
			runtime = 0
			while True:
				cmd = "list vms --show-all; exit"
				ret, output = self.runcmd_rhevm(logger, cmd, "list VMS in rhevm.", rhevm_host_ip)
				runtime = runtime + 1
				if ret == 0 and guest_name in output:
					logger.info("Succeeded to list vm %s." % guest_name)
					status = self.get_key_rhevm(logger, output, "status-state", "name", guest_name, rhevm_host_ip)
					if "down" in status:
						logger.info("Succeeded to import new vm %s to rhevm" % guest_name)
						break
					else :
						logger.info("vm %s status-state is %s" % (guest_name, status))
				time.sleep(10)
				if runtime > 120:
					logger.error("%s status has problem,status is %s." % (guest_name, status))
					self.SET_RESULT(1)

	# import the second guest to rhevm
	def import_sec_vm_to_rhevm(self, logger, guest_name, nfs_dir_for_storage, nfs_dir_for_export, rhevm_host_ip):
		# action vm "6.4_Server_x86_64" import_vm --storagedomain-identifier export_storage  --cluster-name Default --storage_domain-name data_storage
		cmd = "action vm \"%s\" import_vm --storagedomain-identifier %s --cluster-name Default --storage_domain-name %s" % (guest_name, nfs_dir_for_export, nfs_dir_for_storage)
		ret, output = self.runcmd_rhevm(logger, cmd, "import guest %s in rhevm." % guest_name, rhevm_host_ip)
		if ret == 0:
			runtime = 0
			while True:
				cmd = "list vms --show-all; exit"
				ret, output = self.runcmd_rhevm(logger, cmd, "list VMS in rhevm.", rhevm_host_ip)
				runtime = runtime + 1
				if ret == 0 and guest_name in output:
					logger.info("Succeeded to list vm %s." % guest_name)
					status = self.get_key_rhevm(logger, output, "status-state", "name", guest_name, rhevm_host_ip)
					if "down" in status:
						logger.info("Succeeded to import new vm %s to rhevm" % guest_name)
						break
					else :
						logger.info("vm %s status-state is %s" % (guest_name, status))
				time.sleep(10)
				if runtime > 120:
					logger.error("%s status has problem,status is %s." % (guest_name, status))
					self.SET_RESULT(1)

	# Migrate VM on RHEVM
	def rhevm_migrate_guest(self, logger, vm_name, host_name, host_ip, targetmachine_ip):
		cmd = "action vm \"%s\" migrate --host-name \"%s\"" % (vm_name, host_name)
		ret, output = self.runcmd_rhevm(logger, cmd, "migrate vm on rhevm.", targetmachine_ip)
		if self.wait_for_status(logger, "list vms --show-all; exit", "status-state", "up", targetmachine_ip):
			logger.info("Succeeded to start up vm %s." % vm_name)
		else:
			logger.error("Failed to start up vm %s." % vm_name)
			self.SET_RESULT(1)
		if self.wait_for_status(logger, "list vms --show-all; exit", "display-address", host_ip, targetmachine_ip):
			logger.info("Succeeded to migrate vm %s to host %s in rhevm." % (vm_name, host_name))
		else:
			logger.error("Failed to migrate vm %s to host %s in rhevm." % (vm_name, host_name))
			self.SET_RESULT(1)

# Remove VM on RHEVM
	def rhevm_remove_vm(self, logger, vm_name, targetmachine_ip):
		cmd = "remove vm \"%s\" --force" % vm_name
		ret, output = self.runcmd_rhevm(logger, cmd, "Remove VM on RHEVM.", targetmachine_ip)
		if ret == 0:
			timout = 0
			while True:
				timout = timout + 1
				cmd = "list vms; exit"
				(ret, output) = self.runcmd_rhevm(logger, cmd, "list VMS in rhevm.", targetmachine_ip)
				if (ret == 0) and output.find(vm_name) < 0 :
					logger.info("Succeeded to remove vm %s" % vm_name)
					break
				elif timout > 60:
					logger.error("Time out, running rhevm-shell command in server failed.")
					return False
				else:
					logger.error("Failed to remove vm %s" % vm_name)
					self.SET_RESULT(1)

# Add new VM on RHEVM
	def rhevm_add_vm(self, logger, vm_name, targetmachine_ip):
		cmd = "add vm --name %s --template-name Blank --cluster-name Default --memory 536870912; exit" % vm_name
		ret, output = self.runcmd_rhevm(logger, cmd, "add vm to rhevm.", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to add new VM %s." % vm_name)
			runtime = 0
			while True:
				cmd = "list vms --show-all; exit"
				ret, output = self.runcmd_rhevm(logger, cmd, "list VMS in rhevm.", targetmachine_ip)
				runtime = runtime + 1
				if ret == 0:
					logger.info("Succeeded to list vm %s." % vm_name)
					status = self.get_key_rhevm(logger, output, "status-state", "name", vm_name, targetmachine_ip)
					if "up" in status:
						logger.info("Succeeded to up vm %s in rhevm" % vm_name)
						break
					else :
						logger.info("hosts status-state is %s" % status)
					time.sleep(10)
					if runtime > 120:
						logger.error("%s status has problem,status is %s." % (vm_name, status))
						self.SET_RESULT(1)
				else:
					logger.error("Failed to list VM %s." % vm_name)
					self.SET_RESULT(1) 
		else:
			logger.error("Failed to add new VM")
			self.SET_RESULT(1)


# Get guestip
	def rhevm_get_guest_ip(self, logger, vm_name, targetmachine_ip):
		cmd = "list vms --show-all; exit"
		ret, output = self.runcmd_rhevm(logger, cmd, "list VMS in rhevm.", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to list vm %s." % vm_name)
			guestip = self.get_key_rhevm(logger, output, "guest_info-ips-ip-address", "name", vm_name, targetmachine_ip)
			hostuuid = self.get_key_rhevm(logger, output, "host-id", "name", vm_name, targetmachine_ip)
			if guestip is not "":
				logger.info("vm %s ipaddress is %s" % (vm_name, guestip))
				return (guestip, hostuuid)
			else:
				logger.error("Failed to gest the vm %s ipaddress" % vm_name)
		else:
			logger.error("Failed to list VM %s." % vm_name)
			self.SET_RESULT(1) 

# Start VM on RHEVM
	def rhevm_start_vm(self, logger, rhevm_vm_name, targetmachine_ip):
		cmd = "action vm \"%s\" start; exit" % rhevm_vm_name
		ret, output = self.runcmd_rhevm(logger, cmd, "start vm on rhevm.", targetmachine_ip)
		if ret == 0:
			runtime = 0
			while True:
				cmd = "list vms --show-all; exit"
				ret, output = self.runcmd_rhevm(logger, cmd, "list vms in rhevm.", targetmachine_ip)
				runtime = runtime + 1
				if ret == 0:
					logger.info("Succeeded to list vms")
					status = self.get_key_rhevm(logger, output, "status-state", "name", rhevm_vm_name, targetmachine_ip)
					if status.find("up") >= 0 and status.find("powering") < 0 and output.find("guest_info-ips-ip-address") > 0:
						logger.info("Succeeded to up vm %s in rhevm" % rhevm_vm_name)
						time.sleep(10)
						break
					else :
						logger.info("vm %s status-state is %s" % (rhevm_vm_name, status))
					time.sleep(10)
					if runtime > 100:
						logger.error("%s's status has problem,status is %s." % (rhevm_vm_name, status))
						self.SET_RESULT(1)
				else:
					logger.error("Failed to list vm %s" % rhevm_vm_name)
					self.SET_RESULT(1) 
		else:
			logger.error("Failed to start vm %s on rhevm" % rhevm_vm_name)
			self.SET_RESULT(1)

# Stop VM on RHEVM
	def rhevm_stop_vm(self, logger, rhevm_vm_name, targetmachine_ip):
		cmd = "action vm \"%s\" stop; exit" % rhevm_vm_name
		ret, output = self.runcmd_rhevm(logger, cmd, "stop vm on rhevm.", targetmachine_ip)
		if ret == 0:
			runtime = 0
			while True:
				cmd = "list vms --show-all; exit"
				ret, output = self.runcmd_rhevm(logger, cmd, "list vms in rhevm.", targetmachine_ip)
				runtime = runtime + 1
				if ret == 0:
					logger.info("Succeeded to list vms")
					status = self.get_key_rhevm(logger, output, "status-state", "name", rhevm_vm_name, targetmachine_ip)
					if status.find("down") >= 0 and status.find("powering") < 0:
						logger.info("Succeeded to stop vm %s in rhevm" % rhevm_vm_name)
						break
					else :
						logger.info("vm %s status-state is %s" % (rhevm_vm_name, status))
					time.sleep(10)
					if runtime > 120:
						logger.error("%s's status has problem,status is %s." % (rhevm_vm_name, status))
						self.SET_RESULT(1)
				else:
					logger.error("Failed to list vm %s" % rhevm_vm_name)
					self.SET_RESULT(1) 
		else:
			logger.error("Failed to stop vm %s on rhevm" % rhevm_vm_name)
			self.SET_RESULT(1)

# Suspend VM on RHEVM
	def rhevm_suspend_vm(self, logger, rhevm_vm_name, targetmachine_ip):
		cmd = "action vm \"%s\" suspend; exit" % rhevm_vm_name
		ret, output = self.runcmd_rhevm(logger, cmd, "suspend vm on rhevm.", targetmachine_ip)
		if ret == 0:
			runtime = 0
			while True:
				cmd = "list vms --show-all; exit"
				ret, output = self.runcmd_rhevm(logger, cmd, "list vms in rhevm.", targetmachine_ip)
				runtime = runtime + 1
				if ret == 0:
					logger.info("Succeeded to list vms")
					status = self.get_key_rhevm(logger, output, "status-state", "name", rhevm_vm_name, targetmachine_ip)
					if status.find("suspended") >= 0:
						logger.info("Succeeded to suspend vm %s in rhevm" % rhevm_vm_name)
						break
					else :
						logger.info("vm %s status-state is %s" % (rhevm_vm_name, status))
					time.sleep(10)
					if runtime > 120:
						logger.error("%s's status has problem,status is %s." % (rhevm_vm_name, status))
						self.SET_RESULT(1)
				else:
					logger.error("Failed to list vm %s" % rhevm_vm_name)
					self.SET_RESULT(1) 
		else:
			logger.error("Failed to suspend vm %s on rhevm" % rhevm_vm_name)
			self.SET_RESULT(1)

# Shutdown VM on RHEVM
	def rhevm_shutdown_vm(self, logger, rhevm_vm_name, targetmachine_ip):
		cmd = "action vm \"%s\" shutdown; exit" % rhevm_vm_name
		ret, output = self.runcmd_rhevm(logger, cmd, "shutdown vm on rhevm.", targetmachine_ip)
		if ret == 0:
			runtime = 0
			while True:
				cmd = "list vms --show-all; exit"
				ret, output = self.runcmd_rhevm(logger, cmd, "list vms in rhevm.", targetmachine_ip)
				runtime = runtime + 1
				if ret == 0:
					logger.info("Succeeded to list vms")
					status = self.get_key_rhevm(logger, output, "status-state", "name", rhevm_vm_name, targetmachine_ip)
					if status.find("down") >= 0 and status.find("powering") < 0:
						logger.info("Succeeded to shutdown vm %s in rhevm" % rhevm_vm_name)
						break
					else :
						logger.info("vm %s status-state is %s" % (rhevm_vm_name, status))
					time.sleep(10)
					if runtime > 120:
						logger.error("%s's status has problem,status is %s." % (rhevm_vm_name, status))
						self.SET_RESULT(1)
				else:
					logger.error("Failed to list vm %s" % rhevm_vm_name)
					self.SET_RESULT(1) 
		else:
			logger.error("Failed to shutdown vm %s on rhevm" % rhevm_vm_name)
			self.SET_RESULT(1)

	def get_vm_uuid_on_rhevm(self, logger, vm_hostname, targetmachine_ip):
		cmd = "list vms --show-all; exit"
		ret, output = self.runcmd_rhevm(logger, cmd, "list all vms in the rhevm.", targetmachine_ip)
		if ret == 0:
			vm_uuid = self.get_key_rhevm(logger, output, "id", "name", vm_hostname, targetmachine_ip)
			logger.info("%s's uuid is %s" % (vm_hostname, vm_uuid))
			return vm_uuid

	def get_host_uuid_on_rhevm(self, logger, host_hostname, targetmachine_ip):
		cmd = "list hosts --show-all; exit"
		ret, output = self.runcmd_rhevm(logger, cmd, "list all hosts in the rhevm.", targetmachine_ip)
		if ret == 0:
			host_uuid = self.get_key_rhevm(logger, output, "id", "name", host_hostname, targetmachine_ip)
			logger.info("%s's uuid is %s" % (host_hostname, host_uuid))
			return host_uuid

	def rhevm_get_hostuuid_from_list_vm(self, logger, vm_hostname, targetmachine_ip):
		cmd = "list vms --show-all; exit"
		ret, output = self.runcmd_rhevm(logger, cmd, "list all vms in the rhevm.", targetmachine_ip)
		if ret == 0:
			host_uuid = self.get_key_rhevm(logger, output, "host-id", "name", vm_hostname, targetmachine_ip)
			logger.info("%s's host uuid is %s" % (vm_hostname, host_uuid))
			return host_uuid
		
	def rhevm_get_ip_from_hostuuid(self, logger, host_uuid, targetmachine_ip):
		cmd = "list hosts --show-all; exit"
		ret, output = self.runcmd_rhevm(logger, cmd, "list all hosts in the rhevm.", targetmachine_ip)
		if ret == 0:
			host_ip = self.get_key_rhevm(logger, output, "address", "id", host_uuid, targetmachine_ip)
			logger.info("%s's ip address is %s" % (host_uuid, host_ip))
			return host_ip
		else:
			logger.error("Guest failed to auto associate host.")
			self.SET_RESULT(1)

# Check the host and guest uuid in rhsm.log
	def rhevm_vw_check_uuid(self, logger, hostuuid, rhevm_mode, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
	# def vw_check_uuid(self, logger, params, guestname, guestuuid="Default", uuidexists=True, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
		''' check if the guest uuid is correctly monitored by virt-who. '''
		rhsmlogfile = os.path.join(rhsmlogpath, "rhsm.log")
		# self.vw_restart_virtwho(logger)
		cmd = "tail -1 %s " % rhsmlogfile
		ret, output = self.runcmd(logger, cmd, "check output in rhsm.log", targetmachine_ip)
		if ret == 0:
			''' get guest uuid.list from rhsm.log '''
			if "Sending update in hosts-to-guests mapping: " in output:
				log_uuid_list = output.split('Sending update in hosts-to-guests mapping:')[1]
				logger.info("Succeeded to get uuid.list from rhsm.log.")
				if hostuuid is not "":
					hostloc = log_uuid_list.find(hostuuid)
					if rhevm_mode == "rhevm":
						if hostloc >= 0:
							khrightloc = log_uuid_list.find("[", hostloc, -1)
							khleftloc = log_uuid_list.find("]", hostloc, -1)
							# logstring = log_uuid_list[khrightloc,khleftloc]
							ptn = re.compile(r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}')
							ulst = ptn.findall(log_uuid_list[khrightloc:khleftloc])
							guestnum = len(ulst)
							if guestnum >= 0:
							# if logstring.find(guestuuid) >= 0:
								logger.info("host and guest uuid associate correct, host has %s guest" % guestnum)
								return (guestnum, ulst)
						else:
							logger.error("host hasn't find out in the log")
							self.SET_RESULT(1)
					else:
						khrightloc = log_uuid_list.find("[", hostloc, -1)
						khleftloc = log_uuid_list.find("]", hostloc, -1)
						# logstring = log_uuid_list[khrightloc,khleftloc]
						ptn = re.compile(r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}')
						ulst = ptn.findall(log_uuid_list[khrightloc:khleftloc])
						guestnum = len(ulst)
						if guestnum >= 0:
						# if logstring.find(guestuuid) >= 0:
							logger.info("vdsm mode, there are %s hosts" % guestnum)
							return (guestnum, ulst)
			else:
				logger.error("log file has problem, please check it !")
				self.SET_RESULT(1)
				
# Get host num in the rhsm.log file.
	def get_hostnum_rhsmlog(self, logger, rhsmlogpath='/var/log/rhsm', targetmachine_ip=""):
		''' Get the host number. '''
		rhsmlogfile = os.path.join(rhsmlogpath, "rhsm.log")
		# self.vw_restart_virtwho(logger)
		cmd = "tail -1 %s " % rhsmlogfile
		ret, output = self.runcmd(logger, cmd, "check output in rhsm.log", targetmachine_ip)
		if ret == 0:
			''' get host number from rhsm.log '''
			if "Sending update in hosts-to-guests mapping: " in output:
				log_uuid_list = output.split('Sending update in hosts-to-guests mapping:')[1]
				logger.info("Succeeded to get host uuid.list from rhsm.log.")
				if log_uuid_list is not "":
					hostnum = log_uuid_list.count(':')
					logger.info("Succeeded to get the host number, Total host is %s" % hostnum)
					return hostnum
				else:
					logger.error("Succeeded to get the host number")
					

# Get guest uuid in the rhsm.log file.
	def get_guestid_rhsmlog(self, logger, hostname, targetmachine_ip=""):
		''' Get the guestuuid. '''
		cmd = "grep 'Sending update in hosts-to-guests mapping' /var/log/rhsm/rhsm.log | tail -1"
		ret, output = self.runcmd(logger, cmd, "get guest consumer uuid", targetmachine_ip)
		if ret == 0:
			guestuuid = output.split("['")[1].split("']")[0].strip()
			return guestuuid
		else:
			logger.error("Failed to get guestuuid in rhsm.log.")
			self.SET_RESULT(1)

# Get host uuid in the rhsm.log file.
	def get_hostid_rhsmlog(self, logger, hostname, targetmachine_ip=""):
		''' Get the hostuuid. '''
		cmd = "grep 'Sending update in hosts-to-guests mapping' /var/log/rhsm/rhsm.log | tail -1"
		ret, output = self.runcmd(logger, cmd, "get host consumer uuid", targetmachine_ip)
		if ret == 0:
			hostuuid = output.split("{'")[1].split("':")[0].strip()
			return hostuuid
		else:
			logger.error("Failed to get hostuuid in rhsm.log.")
			self.SET_RESULT(1)

	def get_hostid(self, logger, hostname, targetmachine_ip=""):
		''' Get the hostid. '''
		availhostlist = self.sub_listavailhosts(logger, hostname, targetmachine_ip)
		if availhostlist != None:
			for index in range(0, len(availhostlist)):
				if("name" in availhostlist[index] and availhostlist[index]["name"] == hostname):
					rindex = index
					break
			hostid = availhostlist[rindex]["id"]
			logger.info("Succeeded to get the %s's hostid." % hostname)
			return hostid
		else:
			logger.error("Failed to get the %s's hostid." % hostname)
			self.SET_RESULT(1)

	def rhevm_define_guest(self, logger, targetmachine_ip=""):
		''' wget kvm img and xml file, define it in execute machine for converting to rhevm '''
		cmd = "test -d /tmp/rhevm_guest/ && echo presence || echo absence"
		ret, output = self.runcmd(logger, cmd, "check whether guest exist")
		if "presence" in output:
			logger.info("guest has already exist")
		else:
			cmd = "wget -P /tmp/rhevm_guest/ http://10.66.100.116/projects/sam-virtwho/rhevm_guest/6.4_Server_x86_64"
			ret, output = self.runcmd(logger, cmd, "wget kvm img file", targetmachine_ip, showlogger=False)
			if ret == 0:
				logger.info("Succeeded to wget kvm img file")
			else:
				logger.error("Failed to wget kvm img file")
				self.SET_RESULT(1)
		cmd = "wget -P /tmp/rhevm_guest/xml/ http://10.66.100.116/projects/sam-virtwho/rhevm_guest/xml/6.4_Server_x86_64.xml"
		ret, output = self.runcmd(logger, cmd, "wget kvm xml file", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to wget xml img file")
		else:
			logger.error("Failed to wget xml img file")
			self.SET_RESULT(1)
		cmd = "virsh define /tmp/rhevm_guest/xml/6.4_Server_x86_64.xml"
		ret, output = self.runcmd(logger, cmd, "define kvm guest", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to define kvm guest")
		else:
			logger.error("Failed to define kvm guest")
			self.SET_RESULT(1)
			
# Get the host/guest association in the SAM.
	def Rhevm_check_guestinfo_in_host_samserv(self, logger, uuid, non_key_value, key_value, find_value, targetmachine_ip=""):
		''' check rhevm host exist in sam server '''
		cmd = "headpin -u admin -p admin system info --org=ACME_Corporation --uuid=%s" % uuid
		ret, output = self.runcmd(logger, cmd, "list host or guest's system info in the SAM.", targetmachine_ip)
		if ret == 0:
			logger.info("Succeeded to list host or guest's system info on SAM.")
			status = self.get_key_rhevm(logger, output, non_key_value, key_value, find_value, targetmachine_ip)
			return status
		else:
			logger.info("Failed to list host or guest's system info on SAM.")

# Get the uuid in the subscription-manager after register
	def Rhevm_get_uuid_in_submanager(self, logger, targetmachine_ip=""):
		cmd = "subscription-manager identity | grep identity"
		ret, output = self.runcmd(logger, cmd, "get host subscription-manager identity", targetmachine_ip)
		if ret == 0:
			uuid = output.split(':')[1].strip()
			logger.info("Succeeded to get host %s uuid %s " % (targetmachine_ip, uuid))
			return uuid
		else :
			logger.error("Failed to get host %s uuid " % (targetmachine_ip))

	# Check the consumed subscription after auto-assigned to another hosts
	def rhevm_check_consumed_auto_assgin(self, logger, targetmachine_ip):
		''' Register the machine. '''
		cmd = "subscription-manager refresh"
		ret, output = self.runcmd(logger, cmd, "subscription-manager refresh", targetmachine_ip)
		if ret == 0 or "All local data removed" in output:
			logger.info("Succeeded to refresh all data on the system %s" % self.get_HG_info(targetmachine_ip))
		else:
			logger.error("Failed to refresh all data on the system %s" % self.get_HG_info(targetmachine_ip))
			self.SET_RESULT(1)
		''' List consumed entitlements. '''
		cmd = "subscription-manager list --consumed"
		ret, output = self.runcmd(logger, cmd, "list consumed subscriptions", targetmachine_ip)
		if ret == 0 and ("No Consumed" in output or "No consumed" in output):
			logger.info("Succeeded to check no consumed subscription %s." % self.get_HG_info(targetmachine_ip))
		else:
			logger.error("Failed to check no consumed subscription %s." % self.get_HG_info(targetmachine_ip))
			self.SET_RESULT(1)

	def sub_clean(self, logger, targetmachine_ip=""):
		''' Clean all local data. '''
		cmd = "subscription-manager clean"
		ret, output = self.runcmd(logger, cmd, "subscription-manager clean", targetmachine_ip)
		if ret == 0 or "All local data removed" in output:
			logger.info("Succeeded to clean all data on the system %s" % self.get_HG_info(targetmachine_ip))
		else:
			logger.error("Failed to clean all data on the system %s" % self.get_HG_info(targetmachine_ip))
			self.SET_RESULT(1)

	# Clean rhevm env in the rhevm machine.
	def rhevm_clean_env(self, logger, targetmachine_ip=""):
		cmd = "rhevm-cleanup -u"
		ret, output = self.runcmd(logger, cmd, "install vdsm", targetmachine_ip)
		if ret == 0 and "finished successfully" in output:
			logger.info("Succeeded to clean all environment in the rhevm-machine.")
		else:
			logger.info("Failed to clean all environment in the rhevm-machine.")

	# Set up rhevm env in rhevm machine.
	def rhevm_setup_env(self, hostname, username, rhevmhostname, password, cmd):
		""" Remote exec function via pexpect """
		user_hostname = "%s@%s" % (username, hostname)
		child = pexpect.spawn("/usr/bin/ssh", [user_hostname, cmd], timeout=1800, maxread=2000, logfile=None)
		while True:
			index = child.expect(['httpd configuration', 'HTTP Port', 'HTTPS Port', 'fully qualified domain', 'password', 'default storage type', 'DB type', 'NFS share', 'iptables', '(yes\/no)', pexpect.EOF, pexpect.TIMEOUT])
			if index == 0:
				child.sendline("yes")
			elif index == 1:
				child.sendline("80")
			elif index == 2:
				child.sendline("443")
			elif index == 3:
				child.sendline(rhevmhostname)
			elif index == 4:
				child.sendline(password)
			elif index == 5:
				child.sendline("NFS")
			elif index == 6:
				child.sendline("local")
			elif index == 7:
				child.sendline("no")
			elif index == 8:
				child.sendline("iptables")
			elif index == 9:
				child.sendline("yes")
			elif index == 10:
				child.close()
				return child.exitstatus, child.before
			elif index == 11:
				child.close()
				return 1, ""
		return 0
