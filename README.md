## Basic instructions
  
  * Install python requirements
  ```
  python -m pip -r requirements.txt
  ```
  
  * Run the server.py script with Python 3+
  ```
  python server.py
  ```
  
  * Import the spintrhythmtt/project.godot file in Godot
  * Export the Android application as apk and transfer it to your phone (you can find 
    tutorials on how to export to Android with Godot in their documentation or on YouTube)
  * Install the .apk on your phone.

If the python script is running, the knobs in the Android app should tweak the joystick of your vJoy device.
  
## Todo
It would be convenient if an APK build was included in a release, but currently the IP address is hardcoded in the source 
file. The application should perhaps provide an input box for IP and port configuration on startup, or a configuration file.
