extends Control

export(DynamicFont) var font

var sock = PacketPeerUDP.new()

var knobs = []
var margin = 90
var knob_max = 0x8000
var sensitivity
var side

# Holds index of knobs pressed
var pressed_knob = {}

onready var screen = get_viewport().get_visible_rect().size
onready var radius = (screen.y - margin * 2) / 2
onready var sides = [margin + radius, screen.x - margin - radius]


func apply_config():
	var config = $Config.config
	
	sock.close()
	
	# The side of the screen the knob is positioned
	side = config.get_value('style', 'side')
	
	# Initialize the knob
	knobs.clear()
	add_knob(sides[side], config.get_value('style', 'color'))
	
	# Move the config panel
	var config_x = margin if side == 1 else screen.x - margin - ($Config.get_rect().size.x * $Config.get_scale().x)
	$Config.set_position(Vector2(config_x, margin))
	
	# Set the destination address and port, and if successful, start streaming the knob data
	var err = sock.set_dest_address(config.get_value('general', 'host'), config.get_value('general', 'port'))
	if err == OK:
		$AxisTimer.wait_time = 1.0 / config.get_value('general', 'refresh')
		$AxisTimer.start()


func _ready():
	apply_config()


func add_knob(x, color):
	knobs.append({
		'value': 0,
		'position': Vector2(x, screen.y / 2),
		'color': color,
		'press_angle': 0,
		'last_value': 0,
		'active': false
	})


func get_knob(pos):
	for knob in knobs:
		if pos.x > (knob.position.x - radius) and pos.x < (knob.position.x + radius) and pos.y > (knob.position.y - radius) and pos.y < (knob.position.y + radius):
			return knob


func send_axis():
	var button = '1' if knobs[0].active else '0'
	var json = '[' + str(knobs[0].value) + ', ' + button + ']'
	sock.put_packet(json.to_ascii())
	
	
func get_angle(knob, pos):
	return atan2(pos.y - knob.position.y, pos.x - knob.position.x)
	
	
func to_value(rad):
	return int((rad + PI) * knob_max / (2 * PI)) % knob_max


func _input(event):
	if event is InputEventScreenTouch:
		if event.pressed:
			var knob = get_knob(event.position)
			knob.press_angle = get_angle(knob, event.position)
			knob.active = true
			pressed_knob[event.index] = knob
		else:
			var knob = pressed_knob[event.index]
			knob.last_value = knob.value
			knob.active = false
			pressed_knob.erase(event.index)
	
	elif event is InputEventScreenDrag:
		var knob = pressed_knob[event.index]
		var angle = get_angle(knob, event.position)
		knob.value = fposmod(knob.last_value + to_value(angle - knob.press_angle - PI), knob_max)


func _process(delta):
	update()
	
	
func _draw():
	draw_rect(Rect2(0, 0, screen.x, screen.y), Color.black)
	
	for knob in knobs:
		draw_circle(knob.position, radius, knob.color)
		draw_string(font, knob.position, str(knob.value))
