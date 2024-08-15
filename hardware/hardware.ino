const uint8_t pin_left_enl = 2;
const uint8_t pin_left_enr = 3;
const uint8_t pin_left_pwml = 9;
const uint8_t pin_left_pwmr = 8;
const uint8_t pin_right_enl = 6;
const uint8_t pin_right_enr = 7;
const uint8_t pin_right_pwml = 4;
const uint8_t pin_right_pwmr = 5;

const size_t serial_buffer_len = 1024;
uint8_t serial_buffer[serial_buffer_len];

enum states_t {
  header_1,
  header_2,
  motor_left,
  motor_right,
  crc
};

struct packet_t {
  int8_t motor_left;
  int8_t motor_right;
};

states_t current_state = header_1;

packet_t current_packet = {
  .motor_left = 0,
  .motor_right = 0
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
          current_state = motor_left;
        }
        else
        {
          current_state = header_1;
        }
        break;
      case motor_left:
        current_packet.motor_left = data;
        current_state = motor_right;
        break;
      case motor_right:
        current_packet.motor_right = data;
        current_state = crc;
        break;
      case crc:
        const uint8_t calc_crc = current_packet.motor_left ^ current_packet.motor_right;
        if(calc_crc != data) {
          break;
        }

        int val_l = (int)current_packet.motor_left * 2;

        int val_r = (int)current_packet.motor_right * 2;

        if(current_packet.motor_left >= 0) {
          analogWrite(pin_left_pwml, abs(val_l));
          analogWrite(pin_left_pwmr, 0);
        }
        else
        {
          analogWrite(pin_left_pwml, 0);
          analogWrite(pin_left_pwmr, abs(val_l));
        }

        if(current_packet.motor_right >= 0) {
          analogWrite(pin_right_pwml, abs(val_r));
          analogWrite(pin_right_pwmr, 0);
        }
        else
        {
          analogWrite(pin_right_pwml, 0);
          analogWrite(pin_right_pwmr, abs(val_r));
        }

        kill_timer = millis() + kill_timeout_ms;
        Serial.println("Received (" +
                     String(current_packet.motor_left) + ", " +
                     String(current_packet.motor_right) + ", " +
                     String(val_l) + ", " +
                     String(val_r) + ")");

        current_state = header_1;
        break;
    }
  }
}
