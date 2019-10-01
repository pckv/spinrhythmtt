extends Panel

signal config_applied

var config = ConfigFile.new()
var config_path = 'user://settings.cfg'

onready var size = get_rect().size


func save_value(value, section, key):
	if value is float:
		value = int(value)
	
	config.set_value(section, key, value)
	


func get_config():
	var err = config.load(config_path)
	
	if err != OK:
		config.set_value('general', 'host', '127.0.0.1')
		config.set_value('general', 'port', 14854)
		config.set_value('general', 'refresh', 120)
		
		config.set_value('style', 'side', 0)
		config.set_value('style', 'color', Color('#3f63ae'))
		err = config.save(config_path)


func _ready():
	get_config()
	
	$OptionsContainer/HostContainer/HostField.text = config.get_value('general', 'host')
	$OptionsContainer/PortContainer/PortField.value = config.get_value('general', 'port')
	$OptionsContainer/RefreshContainer/RefreshField.value = config.get_value('general', 'refresh')
	
	$OptionsContainer/SideContainer/SideOption.select(config.get_value('style', 'side'))
	$OptionsContainer/ColorContainer/ColorSelect.color = config.get_value('style', 'color')


func apply_config():
	config.save(config_path)
	emit_signal("config_applied")
