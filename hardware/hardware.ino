const uint8_t pin_dir_left = 2;
const uint8_t pin_pwm_left = 3;
const uint8_t pin_dir_right = 4;
const uint8_t pin_pwm_right = 5;

const size_t serial_buffer_len = 1024;
uint8_t serial_buffer[serial_buffer_len];

enum states_t {
  header_1,
  header_2,
  dir_left,
  pwm_left,
  dir_right,
  pwm_right,
  crc
};

struct packet_t {
  uint8_t dir_left;
  uint8_t pwm_left;
  uint8_t dir_right;
  uint8_t pwm_right;
};

states_t current_state = header_1;

packet_t current_packet = {
  .dir_left = 0,
  .pwm_left = 0,
  .dir_right = 0,
  .pwm_right = 0
};

unsigned long heartbeat = 0;

unsigned long kill_time = 1000;
unsigned long kill_timeout = 0;

void setup() {
  pinMode(pin_dir_left, OUTPUT);
  pinMode(pin_pwm_left, OUTPUT);
  pinMode(pin_dir_right, OUTPUT);
  pinMode(pin_pwm_right, OUTPUT);

  digitalWrite(pin_dir_left, LOW);
  digitalWrite(pin_dir_right, LOW);
  digitalWrite(pin_dir_right, LOW);
  digitalWrite(pin_pwm_right, LOW);

  Serial.setTimeout(1);
  Serial.begin(115200);
  Serial.flush();
  Serial.println("Starting");
  delay(10);
}

void loop() {
  if(millis() >= heartbeat) {
    Serial.println("Heartbeat");
    heartbeat = millis() + 1000;
  }
  if(millis() >= kill_timeout) {
    analogWrite(pin_pwm_left, 0);
    analogWrite(pin_pwm_right, 0);
  }

  const size_t bytes_read = Serial.readBytes(serial_buffer, serial_buffer_len);

  for(size_t ii = 0;ii < bytes_read; ++ii) {
    uint8_t data = serial_buffer[ii];

    switch(current_state) {
      case header_1:
        if (data == 0xf0) {
          Serial.println("header_1 found");
          current_state = header_2;
        }
        else
        {
          Serial.println("header_1 failed");
        }
        break;
      case header_2:
        if (data == 0x0f) {
          Serial.println("header_2 found");
          current_state = dir_left;
        }
        else
        {
          Serial.println("header_2 failed");
          current_state = header_1;
        }
        break;
      case dir_left:
        Serial.println("dir_left found");
        current_packet.dir_left = data;
        current_state = pwm_left;
        break;
      case pwm_left:
        Serial.println("pwm_left found");
        current_packet.pwm_left = data;
        current_state = dir_right;
        break;
      case dir_right:
        Serial.println("dir_right found");
        current_packet.dir_right = data;
        current_state = pwm_right;
        break;
      case pwm_right:
        Serial.println("pwm_right found");
        current_packet.pwm_right = data;
        current_state = crc;
        break;
      case crc:
        const uint8_t calc_crc = current_packet.dir_left ^ current_packet.pwm_left ^ current_packet.dir_right ^ current_packet.pwm_right;
        if(calc_crc == data) {
          Serial.println("crc found");
          digitalWrite(pin_dir_left, current_packet.dir_left);
          analogWrite(pin_pwm_left, current_packet.pwm_left);
          digitalWrite(pin_dir_right, current_packet.dir_right);
          analogWrite(pin_pwm_right, current_packet.pwm_right);
          kill_timeout = millis() + kill_time;
        }
        else
        {
          Serial.println("crc failed");
        }
        current_state = header_1;
    }
  }
}
