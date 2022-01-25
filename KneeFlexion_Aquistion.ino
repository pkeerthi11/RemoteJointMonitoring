
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <Wire.h>
#include <utility/imumaths.h>
#include "BluetoothSerial.h"

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

#define BNO055_SAMPLERATE_DELAY_MS (10)

#define SDA1 21
#define SCL1 22

#define SDA2 32
#define SCL2 33

BluetoothSerial SerialBT;

TwoWire I2Cone = TwoWire(0);
TwoWire I2Ctwo = TwoWire(1);
Adafruit_BNO055 bno1 = Adafruit_BNO055(55, 0x28, &I2Cone);
Adafruit_BNO055 bno2 = Adafruit_BNO055(55, 0x28, &I2Ctwo);

void displayCalStatus(void)
{
  /* Get the four calibration values (0..3) */
  /* Any sensor data reporting 0 should be ignored, */
  /* 3 means 'fully calibrated" */
  uint8_t system1, gyro1, accel1, mag1;
  system1 = gyro1 = accel1 = mag1 = 0;
  bno1.getCalibration(&system1, &gyro1, &accel1, &mag1);

  uint8_t system2, gyro2, accel2, mag2;
  system2 = gyro2 = accel2 = mag2 = 0;
  bno2.getCalibration(&system2, &gyro2, &accel2, &mag2);

  /* The data should be ignored until the system calibration is > 0 */
  //Serial.print("\t");
//  if (!system1)
//  {
//    SerialBT.print("! ");
//  }

  /* Display the individual values */
//  SerialBT.print(system1, DEC);
//  SerialBT.print(",");
//  SerialBT.print(gyro1, DEC);
//  SerialBT.print(",");
//  SerialBT.print(accel1, DEC);
//  SerialBT.print(",");
//  SerialBT.print(mag1, DEC);

//  SerialBT.print("\t");
//  if (!system2)
//  {
//    SerialBT.print("! ");
//  }

  /* Display the individual values */
//  SerialBT.print(",");
//  SerialBT.print(system2, DEC);
//  SerialBT.print(",");
//  SerialBT.print(gyro2, DEC);
//  SerialBT.print(",");
//  SerialBT.print(accel2, DEC);
//  SerialBT.print(",");
//  SerialBT.print(mag2, DEC);
}

void setup() {
  Serial.begin(115200);
  I2Cone.begin(SDA1, SCL1, 100000);
  I2Ctwo.begin(SDA2, SCL2, 100000);
  bool status1 = bno1.begin();
  bool status2 = bno2.begin();
  SerialBT.begin("ESP32"); //Bluetooth device name
//  Serial.println("The device started, now you can pair it with bluetooth!");
//  SerialBT.println("Knee Orientation Sensor Data"); Serial.println("");
}


void loop() {
  /*Display calibration status */
  //displayCalStatus();

  /* Gathering data */
  imu::Quaternion quat1 = bno1.getQuat();
  imu::Quaternion quat2 = bno2.getQuat();

  imu::Quaternion quat2_inv = quat2.conjugate()/(quat2.magnitude()*quat2.magnitude());
  imu::Quaternion relative_quat = quat1*quat2_inv;
  imu::Vector<3> euler = relative_quat.toEuler();

//  SerialBT.print(",");
  SerialBT.print(euler.x());
  SerialBT.print(",");
  SerialBT.print(euler.y());
  SerialBT.print(",");
  SerialBT.println(euler.z());
  

  /* New line for the next sample */
  //SerialBT.println("");
  Serial.println(euler.z());
  //Serial.print(",");
  //Serial.print(euler.y());
  //Serial.print(",");
  //Serial.print(euler.z());
  //Serial.println("");
  

  /* Wait the specified delay before requesting nex data */
  delay(BNO055_SAMPLERATE_DELAY_MS);

}
