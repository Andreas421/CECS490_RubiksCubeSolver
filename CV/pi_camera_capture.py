import time

class PiCameraCapture:
	def __init__(self):
		from picamera2 import Picamera2
		from libcamera import controls

		self.camera = Picamera2()
		self.opened = False

		try:
			config = self.camera.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})
			self.camera.configure(config)

			if "AfMode" in self.camera.camera_controls:
				self.camera.set_controls({
					"AfMode": controls.AfModeEnum.Continuous
				})
			self.camera.start()
			self.opened = True
			time.sleep(2)
		except Exception:
			self.camera.close()
			raise

	def isOpened(self):
		return self.opened

	def read(self):
		return True, self.camera.capture_array("main")

	def grab(self):
		self.camera.capture_array("main")
		return True

	def release(self):
		if self.opened:
			try:
				self.camera.stop()
			finally:
				self.camera.close()
				self.opened = False
