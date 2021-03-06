# $language = "python"
# $interface = "1.0"

import os
import sys
import logging

# Add script directory to the PYTHONPATH so we can import our modules (only if run from SecureCRT)
if 'crt' in globals():
    script_dir, script_name = os.path.split(crt.ScriptFullName)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
else:
    script_dir, script_name = os.path.split(os.path.realpath(__file__))

# Now we can import our custom modules
from securecrt_tools import scripts

# Create global logger so we can write debug messages from any function (if debug mode setting is enabled in settings).
logger = logging.getLogger("securecrt")
logger.debug("Starting execution of {0}".format(script_name))


# ################################################   SCRIPT LOGIC   ###################################################

def script_main(session):
    """
    | SINGLE device script
    | Author: Jamie Caesar
    | Email: jcaesar@presidio.com

    This script will grab the output for a list of commands from the connected device.  The list of commands is taken
    from the 'settings/settings.ini' file.  There is a separate list for each supported network operating system (IOS,
    NXOS and ASA).

    | Script Settings (found in settings/settings.ini):
    | folder_per_device - If True, Creates a folder for each device, based on the hostname, and saves all files inside
    |   that folder.  If False, it saves all the files directly into the output folder from the global settings.
    | ios - The list of commands that will be run on IOS devices
    | nxos - The list of commands that will be run on NXOS devices
    | asa - The list of commands that will be run on ASA devices

    The outputs will be saved in a folder named after the hostname of the device, with each output file being saved
    inside that directory.

    :param session: A subclass of the sessions.Session object that represents this particular script session (either
                SecureCRTSession or DirectSession)
    :type session: sessions.Session

    """
    # Get script object that owns this session, so we can check settings, get textfsm templates, etc
    script = session.script

    # Start session with device, i.e. modify term parameters for better interaction (assuming already connected)
    session.start_cisco_session()

    # Validate device is running a supported OS
    session.validate_os(["IOS", "NXOS", "ASA"])

    command_list = script.settings.getlist("document_device", session.os)
    folder_per_device = script.settings.getboolean("document_device", "folder_per_device")

    if folder_per_device:
        output_dir = os.path.join(script.output_dir, session.hostname)
    else:
        output_dir = script.output_dir

    for command in command_list:
        # Generate filename used for output files.
        full_file_name = session.create_output_filename(command, include_hostname=not folder_per_device,
                                                       base_dir=output_dir)
        # Get the output of our command and save it to the filename specified
        session.write_output_to_file(command, full_file_name)

    # Return terminal parameters back to the original state.
    session.end_cisco_session()


# ################################################  SCRIPT LAUNCH   ###################################################

# If this script is run from SecureCRT directly, use the SecureCRT specific class
if __name__ == "__builtin__":
    # Initialize script object
    crt_script = scripts.CRTScript(crt)
    # Get session object for the SecureCRT tab that the script was launched from.
    crt_session = crt_script.get_main_session()
    # Run script's main logic against our session
    script_main(crt_session)
    # Shutdown logging after
    logging.shutdown()

# If the script is being run directly, use the simulation class
elif __name__ == "__main__":
    # Initialize script object
    direct_script = scripts.DebugScript(os.path.realpath(__file__))
    # Get a simulated session object to pass into the script.
    sim_session = direct_script.get_main_session()
    # Run script's main logic against our session
    script_main(sim_session)
    # Shutdown logging after
    logging.shutdown()