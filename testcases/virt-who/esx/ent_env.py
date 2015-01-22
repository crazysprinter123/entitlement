import os

class ent_env:

	# ========================================================
	# 	1. Sub-Man Testing Parameters
	# ========================================================

	# [A] Global parameters
	proxy = "squid.corp.redhat.com:3128"
	username_qa = "qa@redhat.com"
	# password_qa = "8AwpGrI4VO9M"
	# password_qa = "29W11uh4tdq7783"
	password_qa = "AeGh8phugee5"

	# [B] Acceptance/Smoke Test parameters
	# #RHEL-Client-6.2
	username1 = "stage_test_25"
	password1 = "redhat"
	autosubprod1 = "Red Hat Enterprise Linux Desktop"
	installedproductname1 = "Red Hat Enterprise Linux Desktop"
	productid1 = "RH0844913"
	pid1 = "68"
	pkgtoinstall1 = "gnutls-utils"
	productrepo1 = "rhel-6-desktop-rpms"
	betarepo1 = "rhel-6-desktop-beta-rpms"

	# #RHEL-Server-6.2
	username2 = "stage_test_12"
	password2 = "redhat"
	autosubprod2 = "Red Hat Enterprise Linux Server"
	installedproductname2 = "Red Hat Enterprise Linux Server"
	productid2 = "RH0103708"
	pid2 = "69"
	pkgtoinstall2 = "gnutls-utils"
	productrepo2 = "rhel-6-server-rpms"
	betarepo2 = "rhel-6-server-beta-rpms"

	# #RHEL-Client-5.8
	username3 = "stage_test_25"
	password3 = "redhat"
	autosubprod3 = "Red Hat Enterprise Linux Desktop"
	installedproductname3 = "Red Hat Enterprise Linux Desktop"
	productid3 = "RH0844913"
	pid3 = "68"
	pkgtoinstall3 = "zsh"
	productrepo3 = "rhel-5-desktop-rpms"
	betarepo3 = "rhel-5-desktop-beta-rpms"

	# #RHEL-Server-5.8
	username4 = "stage_test_12"
	password4 = "redhat"
	autosubprod4 = "Red Hat Enterprise Linux Server"
	installedproductname4 = "Red Hat Enterprise Linux Server"
	productid4 = "RH0103708"
	pid4 = "69"
	pkgtoinstall4 = "zsh"
	productrepo4 = "rhel-5-server-rpms"
	betarepo4 = "rhel-5-server-beta-rpms"

	# #RHEL-Workstation-5.8
	username5 = "stage_test_27"
	password5 = "redhat"
	autosubprod5 = "Red Hat Enterprise Linux Workstation"
	installedproductname5 = "Red Hat Enterprise Linux Workstation"
	productid5 = "RH0958488"
	pid5 = "71"
	pkgtoinstall5 = "zsh"
	productrepo5 = "rhel-5-workstation-rpms"
	betarepo5 = "rhel-5-workstation-beta-rpms"

	# [C] SAM Test parameters
	# #RHEL-Client-5
	username1s = "admin"
	password1s = "admin"
	autosubprod1s = "Red Hat Enterprise Linux Desktop"
	installedproductname1s = "Red Hat Enterprise Linux Desktop"
	productid1s = "RH0823221"
	pid1s = "68"
	pkgtoinstall1s = "zsh"
	productrepo1s = "rhel-5-desktop-rpms"
	betarepo1s = "rhel-5-desktop-beta-rpms"

	# #RHEL-Server-5
	username2s = "admin"
	password2s = "admin"
	autosubprod2s = "Red Hat Enterprise Linux Server"
	installedproductname2s = "Red Hat Enterprise Linux Server"
	productid2s = "RH0197181"
	pid2s = "69"
	pkgtoinstall2s = "zsh"
	productrepo2s = "rhel-5-server-rpms"
	betarepo2s = "rhel-5-server-beta-rpms"

	# #RHEL-Workstation-5
	username3s = "admin"
	password3s = "admin"
	autosubprod3s = "Red Hat Enterprise Linux Workstation"
	installedproductname3s = "Red Hat Enterprise Linux Workstation"
	productid3s = "RH0958488"
	pid3s = "71"
	pkgtoinstall3s = "zsh"
	productrepo3s = "rhel-5-workstation-rpms"
	betarepo3s = "rhel-5-workstation-beta-rpms"

	# #RHEL-Server-6
	username4s = "admin"
	password4s = "admin"
	autosubprod4s = "Red Hat Enterprise Linux Server"

	# #RHEL-Workstation-6
	username5s = "admin"
	password5s = "admin"

	# virt-who stage candlepin test
	username_stage = "stage_sam_test"
	password_stage = "redhat"

	# ========================================================
	# 	2. SAM Server Testing Parameters
	# ========================================================

	prior_env = "Library"
	default_org = "ACME_Corporation"
	default_env = "env1"
	default_provider = "Red Hat"
	default_provider_repo_url = "https://cdn.redhat.com"
	default_manifest = "default-manifest.zip"

	username1 = "sam_test_1"
	password1 = "redhat"
	email1 = "sam_test_1@localhost"
	org1 = "test_org1"
	env1 = "test_env1"
	keyname1 = "test_key1"
	systemname1 = "system_1"

	password2 = "localhost"
	email2 = "sam_test_1@redhat.com"
	env2 = "test_env100"
	keyname2 = "test_key2"
	systemname2 = "system_2"

	manifest1 = "hss-qe-sam20111213.zip"
	manifest1_product1 = "Red Hat Enterprise Linux Server"
	manifest1_product2 = "Red Hat Enterprise Linux High Availability for RHEL Server"
	manifest2 = "hss-qe-sam20111213-update1-remove.zip"
	manifest3 = "hss-qe-sam20111213-update2-add.zip"
	specific_manifest = "rhel6.2-sam-htb.zip"

	# ========================================================
	# 	3. Virt-Who Testing Parameters
	# ========================================================
	# used for ESX automation
	esx_host_ip = "10.66.128.163"
	vmware_cmd_ip = "10.66.79.88"
	data_store_name = "datastore*"
	# All subscriptions in SAM server
	# limited subscription
	productid_guest = "RH0604852"
	productname_guest = "Red Hat Enterprise Linux Server for HPC Compute Node"
	guestlimit = "1"
	# unlimited subscription
	productid_unlimited_guest = "SYS0395"
	productname_unlimited_guest = "Red Hat Employee Subscription"
	guestlimit_unlimited_guest = "Unlimited"

	# unlimited subscription
	stage_unlimited_guest_SKU = "RH00060"
	stage_unlimited_guest_SubscriptionName = "Resilient Storage for Unlimited Guests"
	stage_unlimited_guest_Available = "Unlimited"
	# stage_unlimited_guest_derived_SKU = "RH00049"
	# limited subscription
	stage_limited_guest_SKU = "MCTTEST1"
	stage_limited_guest_SubscriptionName = "Red Hat Enterprise Linux for Virtual Datacenters, Premium"
	stage_limited_guest_Available = "2"
	# stage_limited_guest_derived_SKU = ""

	# Virtualization subscription
	productid_Virtual_guest = "RV0145582"
	productname_Virtual_guest = "Red Hat Enterprise Virtualization for Desktops"

	# Data center subscription
	data_center_SKU = "RH00002"
	data_center_subscription_name = "Red Hat Enterprise Linux for Virtual Datacenters, Standard"

	# instance subscription
	instance_SKU = "RH00003"
	instance_subscription_name = "Red Hat Enterprise Linux Server, Premium"

	# image source machine information
	image_machine_ip = "10.66.100.116:/data/projects/sam-virtwho/pub"
	beaker_image_machine_ip = "10.16.96.131:/home/samdata"
	image_machine_username = ""
	image_machine_password = ""
	image_machine_imagepath = "ENT_TEST_MEDIUM/images"
	# set dir name which is used to mount the target machine rhsm log
	rhsmlog_for_targetmachine = "/home/ENT_TEST_MEDIUM/rhsmlog"

	# Note: make sure all the guest names are different with each other.
	imagenfspath = "/home/ENT_TEST_MEDIUM/imagenfs"
	imagepath = "/home/ENT_TEST_MEDIUM/images"
	imagepath_kvm = "/home/ENT_TEST_MEDIUM/images/kvm"
	imagepath_xen_pv = "/home/ENT_TEST_MEDIUM/images/xen/xen-pv"
	imagepath_xen_fv = "/home/ENT_TEST_MEDIUM/images/xen/xen-fv"

# # Common Functions ##
	def get_all_guests_list(self, path):
		''' get all guest name from directory '''
		return os.listdir(path)

	def get_env(self, params):

		samhostname = params.get("samhostname")
		samhostip = params.get("samhostip")
		guest_name = params.get("guest_name")
		env = {}

		if samhostname == None or samhostip == None:
			if "RHEL-Client-6" in guest_name:
				env["username"] = self.username1
				env["password"] = self.password1
				env["autosubprod"] = self.autosubprod1
				env["installedproductname"] = self.installedproductname1
				env["productid"] = self.productid1
				env["pid"] = self.pid1
				env["pkgtoinstall"] = self.pkgtoinstall1
				env["productrepo"] = self.productrepo1
				env["betarepo"] = self.betarepo1

			elif "RHEL-Server-6" in guest_name:
				env["username"] = self.username2
				env["password"] = self.password2
				env["autosubprod"] = self.autosubprod2
				env["installedproductname"] = self.installedproductname2
				env["productid"] = self.productid2
				env["pid"] = self.pid2
				env["pkgtoinstall"] = self.pkgtoinstall2
				env["productrepo"] = self.productrepo2
				env["betarepo"] = self.betarepo2

			elif "RHEL-Client-5" in guest_name:
				env["username"] = self.username3
				env["password"] = self.password3
				env["autosubprod"] = self.autosubprod3
				env["installedproductname"] = self.installedproductname3
				env["productid"] = self.productid3
				env["pid"] = self.pid3
				env["pkgtoinstall"] = self.pkgtoinstall3
				env["productrepo"] = self.productrepo3
				env["betarepo"] = self.betarepo3

			elif "RHEL-Server-5" in guest_name:
				env["username"] = self.username4
				env["password"] = self.password4
				env["autosubprod"] = self.autosubprod4
				env["installedproductname"] = self.installedproductname4
				env["productid"] = self.productid4
				env["pid"] = self.pid4
				env["pkgtoinstall"] = self.pkgtoinstall4
				env["productrepo"] = self.productrepo4
				env["betarepo"] = self.betarepo4

			elif "RHEL-Workstation-5" in guest_name:
				env["username"] = self.username5
				env["password"] = self.password5
				env["autosubprod"] = self.autosubprod5
				env["installedproductname"] = self.installedproductname5
				env["productid"] = self.productid5
				env["pid"] = self.pid5
				env["pkgtoinstall"] = self.pkgtoinstall5
				env["productrepo"] = self.productrepo5
				env["betarepo"] = self.betarepo5
		else:
			if "RHEL-Client-5" in guest_name:
				env["username"] = self.username1s
				env["password"] = self.password1s
				env["autosubprod"] = self.autosubprod1s
				env["installedproductname"] = self.installedproductname1s
				env["productid"] = self.productid1s
				env["pid"] = self.pid1s
				env["pkgtoinstall"] = self.pkgtoinstall1s
				env["productrepo"] = self.productrepo1s
				env["betarepo"] = self.betarepo1s

			elif "RHEL-Server-5" in guest_name:
				env["username"] = self.username2s
				env["password"] = self.password2s
				env["autosubprod"] = self.autosubprod2s
				env["installedproductname"] = self.installedproductname2s
				env["productid"] = self.productid2s
				env["pid"] = self.pid2s
				env["pkgtoinstall"] = self.pkgtoinstall2s
				env["productrepo"] = self.productrepo2s
				env["betarepo"] = self.betarepo2s

			elif "RHEL-Workstation-5" in guest_name:
				env["username"] = self.username3s
				env["password"] = self.password3s
				env["autosubprod"] = self.autosubprod3s
				env["installedproductname"] = self.installedproductname3s
				env["productid"] = self.productid3s
				env["pid"] = self.pid3s
				env["pkgtoinstall"] = self.pkgtoinstall3s
				env["productrepo"] = self.productrepo3s
				env["betarepo"] = self.betarepo3s
		return env
