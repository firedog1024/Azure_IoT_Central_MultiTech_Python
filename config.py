# These are the values that need to be configured specifically for your IoT Central application
# The values can be found in Administration -> Device Connection page

# Note:  The APP_KEY allows the device key to be computed in the code.  In a gateway scenario this allows 
# leaf devices to be added to IoT Central without having to first add them to the IoT Central application.
# the code will register the device automatically and it will be placed in the unassociated devices within the 
# Device Explorer page.

# It is also possible to use a model identifier to associate a device with a temmplate within IoT Central.  This allows 
# a device to be auto associated and auto assigned to a template if turned on within the application.  This feature requires
# a manual config change on the application to enable it, please contact IoT Central team if you wish to use this feature 

# Scope identifier for the application - found in IoT Central in the Administration -> Device Connection page
SCOPE_ID = '<insert scope identifier here>'

# Application key - found in IoT Central in the Administration -> Device Connection page
APP_KEY = '<insert application key here>'

# template model identifier - found in IoT Central in the Device Explorer at the top of the page
MODEL_ID = ''

# device identity, this can be pre registered in the IoT Central application or will be registered via DPS and 
# placed in the Unassociated Devices page waiting to be associated with a template
DEVICE_NAME = '<insert device identifier here>'

# how long should the SAS Token be valid for in seconds, code should be added to renew the token before expiration
SAS_TOKEN_TTL = 3600 # one hour

# path to the root cert for Azure services
PATH_TO_ROOT_CERT = 'baltimore.cer'

# validate the cert returned from Azure service
VALIDATE_CERT =  True