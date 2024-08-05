const uint8_t pin_left_enl = 2;
const uint8_t pin_left_enr = 3;
const uint8_t pin_left_pwml = 4;
const uint8_t pin_left_pwmr = 5;
const uint8_t pin_right_enl = 6;
const uint8_t pin_right_enr = 7;
const uint8_t pin_right_pwml = 9;
const uint8_t pin_right_pwmr = 8;

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

unsigned long kill_timer = 0;
unsigned long kill_timeout_ms = 1000;

void setup() {
  pinMode(pin_left_enl, OUTPUT);
  pinMode(pin_left_enr, OUTPUT);
  pinMode(pin_left_pwml, OUTPUT);
  pinMode(pin_left_pwmr, OUTPUT);
  digitalWrite(pin_left_enl, HIGH);
  digitalWrite(pin_left_enr, HIGH);
  analogWrite(pin_left_pwml, 0);
  analogWrite(pin_left_pwmr, 0);

  pinMode(pin_right_enl, OUTPUT);
  pinMode(pin_right_enr, OUTPUT);
  pinMode(pin_right_pwml, OUTPUT);
  pinMode(pin_right_pwmr, OUTPUT);
  digitalWrite(pin_right_enl, HIGH);
  digitalWrite(pin_right_enr, HIGH);
  analogWrite(pin_right_pwml, 0);
  analogWrite(pin_right_pwmr, 0);

  Serial.setTimeout(1);
  Serial.begin(115200);
  Serial.flush();
  Serial.println("Starting");
  delay(10);
}

void loop() {
  if(millis() >= kill_timer) {
    analogWrite(pin_left_pwml, 0);
    analogWrite(pin_left_pwmr, 0);
    analogWrite(pin_right_pwml, 0);
    analogWrite(pin_right_pwmr, 0);
  }

  const size_t bytes_read = Serial.readBytes(serial_buffer, serial_buffer_len);

  for(size_t ii = 0;ii < bytes_read; ++ii) {
    uint8_t data = serial_buffer[ii];

    switch(current_state) {
      case header_1:
        if (data == 0xf0) {
          current_state = header_2;
        }
        break;
      case header_2:
        if (data == 0x0f) {
          current_state = dir_left;
        }
        else
        {
          current_state = header_1;
        }
        break;
      case dir_left:
        current_packet.dir_left = data;
        current_state = pwm_left;
        break;
      case pwm_left:
        current_packet.pwm_left = data;
        current_state = dir_right;
        break;
      case dir_right:
        current_packet.dir_right = data;
        current_state = pwm_right;
        break;
      case pwm_right:
        current_packet.pwm_right = data;
        current_state = crc;
        break;
      case crc:
        const uint8_t calc_crc = current_packet.dir_left ^
                                 current_packet.pwm_left ^
                                 current_packet.dir_right ^
                                 current_packet.pwm_right;
        if(calc_crc != data) {
          break;
        }

        if(current_packet.dir_left == 0) {
          analogWrite(pin_left_pwml, current_packet.pwm_left);
          analogWrite(pin_left_pwmr, 0);
        }
        else
        {
          analogWrite(pin_left_pwml, 0);
          analogWrite(pin_left_pwmr, current_packet.pwm_left);
        }

        if(current_packet.dir_right == 0) {
          analogWrite(pin_right_pwml, current_packet.pwm_right);
          analogWrite(pin_right_pwmr, 0);
        }
        else
        {
          analogWrite(pin_right_pwml, 0);
          analogWrite(pin_right_pwmr, current_packet.pwm_right);
        }

        kill_timer = millis() + kill_timeout_ms;
        Serial.println("Received (" +
                     String(current_packet.dir_left) + ", " +
                     String(current_packet.pwm_left) + ", " +
                     String(current_packet.dir_right) + ", " +
                     String(current_packet.pwm_right) + ")");

        current_state = header_1;
        break;
    }
  }
}
