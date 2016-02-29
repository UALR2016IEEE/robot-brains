import wiringpi2 as wiringpi
import const


class APDS9960:
    def __init__(self):
        pass

    def initialize(self):
        self._fd = wiringpi.wiringPiI2CSetup(const.APDS9960_I2C_ADDR)

        if self.wireReadDataByte(const.APDS9960_ID) not in const.APDS9960_IDs:
            raise IOError

        #Set ENABLE register to 0 (disable all features)
        self.setMode(const.ALL, const.OFF)
        #Set default values for ambient light and proximity registers */
        self.wireWriteDataByte(const.APDS9960_ATIME, const.DEFAULT_ATIME)
        self.wireWriteDataByte(const.APDS9960_WTIME, const.DEFAULT_WTIME)
        self.wireWriteDataByte(const.APDS9960_PPULSE, const.DEFAULT_PROX_PPULSE)
        self.wireWriteDataByte(const.APDS9960_POFFSET_UR, const.DEFAULT_POFFSET_UR)
        self.wireWriteDataByte(const.APDS9960_POFFSET_DL, const.DEFAULT_POFFSET_DL)
        self.wireWriteDataByte(const.APDS9960_CONFIG1, const.DEFAULT_CONFIG1)
        self.setLEDDrive(const.DEFAULT_LDRIVE)

    def wireWriteByte(self, val):
        wiringpi.wiringPiI2CWrite(self._fd, val)

    # /**
    # * @brief Writes a single byte to the I2C device and specified register
    # *
    # * @param[in] reg the register in the I2C device to write to
    # * @param[in] val the 1-byte value to write to the I2C device
    # * @return True if successful write operation. False otherwise.
    # */
    def wireWriteDataByte(self, reg, val):
        wiringpi.wiringPiI2CWriteReg8(self._fd, reg, val)

    # /**
    # * @brief Writes a block (array) of bytes to the I2C device and register
    # *
    # * @param[in] reg the register in the I2C device to write to
    # * @param[in] val pointer to the beginning of the data byte array
    # * @param[in] len the length (in bytes) of the data to write
    # * @return True if successful write operation. False otherwise.
    # */
    def wireWriteDataBlock(self, reg, val):
            wiringpi.wiringPiI2CWrite(self._fd, reg)
            for i in val:
                wiringpi.wiringPiI2CWrite(self._fd, i)


    # * @brief Reads a single byte from the I2C device and specified register
    # *
    # * @param[in] reg the register to read from
    # * @param[out] the value returned from the register
    # * @return True if successful read operation. False otherwise.
    # */
    def wireReadDataByte(self, reg):
        return wiringpi.wiringPiI2CReadReg8(self._fd, reg)

    # * @brief Reads a block (array) of bytes from the I2C device and register
    # *
    # * @param[in] reg the register to read from
    # * @param[out] val pointer to the beginning of the data
    # * @param[in] len number of bytes to read
    # * @return Number of bytes read. -1 on read error.
    # */
    def wireReadDataBlock(self, reg, len):
        wiringpi.wiringPiI2CWrite(self._fd, reg)
        vals = [wiringpi.wiringPiI2CRead(self._fd) for val in range(len)]
        return vals
    # }
    # /*******************************************************************************
    # * Public methods for controlling the APDS-9960
    # ******************************************************************************/
    #
    # /**
    # * @brief Reads and returns the contents of the ENABLE register
    # *
    # * @return Contents of the ENABLE register. 0xFF if error.

    def get_mode(self):
        return wiringpi.wireReadDataByte(const.APDS9960_ENABLE)

    def set_mode(self, mode, enable):
        enable &= 0x01
        reg_val = self.get_mode()
        if 0 <= mode <= 6:
            if enable:
                reg_val |= 1 << mode
            else:
                reg_val &= ~(1 << mode)
        elif mode == const.ALL:
            if enable:
                reg_val = 0x7F
            else:
                reg_val = 0x00

        wiringpi.wireWriteDataByte(const.APDS9960_ENABLE, reg_val)
    #
    # /**
    # * @brief Starts the light (R/G/B/Ambient) sensor on the APDS-9960
    # *
    # * @param[in] interrupts true to enable hardware interrupt on high or low light
    # * @return True if sensor enabled correctly. False on error.
    # */
    def enable_light_sensor(self):
    # 	/* Set default gain, interrupts, enable power, and enable sensor */
        #self.setAmbientLightGain(const.DEFAULT_AGAIN)
        self.enablePower()
        self.set_mode(const.AMBIENT_LIGHT, 1)

    # /**
    # * @brief Ends the light sensor on the APDS-9960
    # *
    # * @return True if sensor disabled correctly. False on error.
    # */
    def disable_light_sensor(self):
        self.set_mode(const.AMBIENT_LIGHT, 0)

    # * @brief Starts the proximity sensor on the APDS-9960
    # *
    # * @param[in] interrupts true to enable hardware external interrupt on proximity
    # * @return True if sensor enabled correctly. False on error.
    def enableProximitySensor(self, interrupts):
        # {
        # 	/* Set default gain, LED, interrupts, enable power, and enable sensor */
        # */

        self.enablePower()
        self.set_mode(const.PROXIMITY, 1)

    # * Turn the APDS-9960 on
    # *
    # * @return True if operation successful. False otherwise.
    # */
    def enablePower(self):
        self.set_mode(const.POWER, 1)

    # /**
    # * Turn the APDS-9960 off
    # *
    # * @return True if operation successful. False otherwise.
    # */
    def disablePower(self):
        self.set_mode(const.POWER, 0)

    # /*******************************************************************************
    # * Ambient light and color sensor controls
    # ******************************************************************************/
    #
    # /**
    # * @brief Reads the ambient (clear) light level as a 16-bit value
    # *
    # * @param[out] val value of the light sensor.
    # * @return True if operation successful. False otherwise.
    # */
    def readAmbientLight(self):
        # 	/* Read value from clear channel, low byte register */
    	lowval = wiringpi.wireReadDataByte(const.APDS9960_CDATAL)
        # 	/* Read value from clear channel, high byte register *
        highval = wiringpi.wireReadDataByte(const.APDS9960_CDATAH)
        lowval += highval << 8
        return lowval

    # * @brief Reads the red light level as a 16-bit value
    # *
    # * @param[out] val value of the light sensor.
    # * @return True if operation successful. False otherwise.
    # */
    def readRedLight(self):
        lowval = self.wireReadDataByte(const.APDS9960_RDATAL)

        # 	/* Read value from clear channel, high byte register */
        highval = self.wireReadDataByte(const.APDS9960_RDATAH)
        lowval += highval << 8
        return lowval
    # * @brief Reads the red light level as a 16-bit value
    # *
    # * @param[out] val value of the light sensor.
    # * @return True if operation successful. False otherwise.
    # */
    def readGreenLight(self):
        lowval = self.wireReadDataByte(const.APDS9960_GDATAL)

        # 	/* Read value from clear channel, high byte register */
        highval = self.wireReadDataByte(const.APDS9960_GDATAH)
        lowval += highval << 8
        return lowval
    # * @brief Reads the red light level as a 16-bit value
    # *
    # * @param[out] val value of the light sensor.
    # * @return True if operation successful. False otherwise.
    # */
    def readBLueLight(self):
        lowval = self.wireReadDataByte(const.APDS9960_RDATAL)

        # 	/* Read value from clear channel, high byte register */
        highval = self.wireReadDataByte(const.APDS9960_RDATAH)
        lowval += highval << 8
        return lowval

    # /*******************************************************************************
    # * Proximity sensor controls
    # ******************************************************************************/
    #
    # /**
    # * @brief Reads the proximity level as an 8-bit value
    # *
    # * @param[out] val value of the proximity sensor.
    # * @return True if operation successful. False otherwise.
    # */
    def readProximity(self):
        return wiringpi.wireReadDataByte(const.APDS9960_PDATA)

    # bool APDS9960_RPi::setProxIntHighThresh(uint8_t threshold)
    # {
    # 	if( !wireWriteDataByte(APDS9960_PIHT, threshold) ) {
    # 		return false;
    # 	}
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Returns LED drive strength for proximity and ALS
    # *
    # * Value    LED Current
    # *   0        100 mA
    # *   1         50 mA
    # *   2         25 mA
    # *   3         12.5 mA
    # *
    # * @return the value of the LED drive strength. 0xFF on failure.
    # */
    # uint8_t APDS9960_RPi::getLEDDrive()
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from CONTROL register */
    # 	if( !wireReadDataByte(APDS9960_CONTROL, val) ) {
    # 		return ERROR;
    # 	}
    #
    # 	/* Shift and mask out LED drive bits */
    # 	val = (val >> 6) & 0b00000011;
    #
    # 	return val;
    # }
    #
    # /**
    # * @brief Sets the LED drive strength for proximity and ALS
    # *
    # * Value    LED Current
    # *   0        100 mA
    # *   1         50 mA
    # *   2         25 mA
    # *   3         12.5 mA
    # *
    # * @param[in] drive the value (0-3) for the LED drive strength
    # * @return True if operation successful. False otherwise.
    # */
    # bool APDS9960_RPi::setLEDDrive(uint8_t drive)
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from CONTROL register */
    # 	if( !wireReadDataByte(APDS9960_CONTROL, val) ) {
    # 		return false;
    # 	}
    #
    # 	/* Set bits in register to given value */
    # 	drive &= 0b00000011;
    # 	drive = drive << 6;
    # 	val &= 0b00111111;
    # 	val |= drive;
    #
    # 	/* Write register value back into CONTROL register */
    # 	if( !wireWriteDataByte(APDS9960_CONTROL, val) ) {
    # 		return false;
    # 	}
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Returns receiver gain for proximity detection
    # *
    # * Value    Gain
    # *   0       1x
    # *   1       2x
    # *   2       4x
    # *   3       8x
    # *
    # * @return the value of the proximity gain. 0xFF on failure.
    # */
    # uint8_t APDS9960_RPi::getProximityGain()
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from CONTROL register */
    # 	if( !wireReadDataByte(APDS9960_CONTROL, val) ) {
    # 		return ERROR;
    # 	}
    #
    # 	/* Shift and mask out PDRIVE bits */
    # 	val = (val >> 2) & 0b00000011;
    #
    # 	return val;
    # }
    #
    # /**
    # * @brief Sets the receiver gain for proximity detection
    # *
    # * Value    Gain
    # *   0       1x
    # *   1       2x
    # *   2       4x
    # *   3       8x
    # *
    # * @param[in] drive the value (0-3) for the gain
    # * @return True if operation successful. False otherwise.
    # */
    # bool APDS9960_RPi::setProximityGain(uint8_t drive)
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from CONTROL register */
    # 	if( !wireReadDataByte(APDS9960_CONTROL, val) ) {
    # 		return false;
    # 	}
    #
    # 	/* Set bits in register to given value */
    # 	drive &= 0b00000011;
    # 	drive = drive << 2;
    # 	val &= 0b11110011;
    # 	val |= drive;
    #
    # 	/* Write register value back into CONTROL register */
    # 	if( !wireWriteDataByte(APDS9960_CONTROL, val) ) {
    # 		return false;
    # 	}
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Returns receiver gain for the ambient light sensor (ALS)
    # *
    # * Value    Gain
    # *   0        1x
    # *   1        4x
    # *   2       16x
    # *   3       64x
    # *
    # * @return the value of the ALS gain. 0xFF on failure.
    # */
    # uint8_t APDS9960_RPi::getAmbientLightGain()
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from CONTROL register */
    # 	if( !wireReadDataByte(APDS9960_CONTROL, val) ) {
    # 		return ERROR;
    # 	}
    #
    # 	/* Shift and mask out ADRIVE bits */
    # 	val &= 0b00000011;
    #
    # 	return val;
    # }
    #
    # /**
    # * @brief Sets the receiver gain for the ambient light sensor (ALS)
    # *
    # * Value    Gain
    # *   0        1x
    # *   1        4x
    # *   2       16x
    # *   3       64x
    # *
    # * @param[in] drive the value (0-3) for the gain
    # * @return True if operation successful. False otherwise.
    # */
    # bool APDS9960_RPi::setAmbientLightGain(uint8_t drive)
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from CONTROL register */
    # 	if( !wireReadDataByte(APDS9960_CONTROL, val) ) {
    # 		return false;
    # 	}
    #
    # 	/* Set bits in register to given value */
    # 	drive &= 0b00000011;
    # 	val &= 0b11111100;
    # 	val |= drive;
    #
    # 	/* Write register value back into CONTROL register */
    # 	if( !wireWriteDataByte(APDS9960_CONTROL, val) ) {
    # 		return false;
    # 	}
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Get the current LED boost value
    # *
    # * Value  Boost Current
    # *   0        100%
    # *   1        150%
    # *   2        200%
    # *   3        300%
    # *
    # * @return The LED boost value. 0xFF on failure.
    # */
    # uint8_t APDS9960_RPi::getLEDBoost()
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from CONFIG2 register */
    # 	if( !wireReadDataByte(APDS9960_CONFIG2, val) ) {
    # 		return ERROR;
    # 	}
    #
    # 	/* Shift and mask out LED_BOOST bits */
    # 	val = (val >> 4) & 0b00000011;
    #
    # 	return val;
    # }
    #
    # /**
    # * @brief Sets the LED current boost value
    # *
    # * Value  Boost Current
    # *   0        100%
    # *   1        150%
    # *   2        200%
    # *   3        300%
    # *
    # * @param[in] drive the value (0-3) for current boost (100-300%)
    # * @return True if operation successful. False otherwise.
    # */
    # bool APDS9960_RPi::setLEDBoost(uint8_t boost)
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from CONFIG2 register */
    # 	if( !wireReadDataByte(APDS9960_CONFIG2, val) ) {
    # 		return false;
    # 	}
    #
    # 	/* Set bits in register to given value */
    # 	boost &= 0b00000011;
    # 	boost = boost << 4;
    # 	val &= 0b11001111;
    # 	val |= boost;
    #
    # 	/* Write register value back into CONFIG2 register */
    # 	if( !wireWriteDataByte(APDS9960_CONFIG2, val) ) {
    # 		return false;
    # 	}
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Gets proximity gain compensation enable
    # *
    # * @return 1 if compensation is enabled. 0 if not. 0xFF on error.
    # */
    # uint8_t APDS9960_RPi::getProxGainCompEnable()
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from CONFIG3 register */
    # 	if( !wireReadDataByte(APDS9960_CONFIG3, val) ) {
    # 		return ERROR;
    # 	}
    #
    # 	/* Shift and mask out PCMP bits */
    # 	val = (val >> 5) & 0b00000001;
    #
    # 	return val;
    # }
    #
    # /**
    # * @brief Sets the proximity gain compensation enable
    # *
    # * @param[in] enable 1 to enable compensation. 0 to disable compensation.
    # * @return True if operation successful. False otherwise.
    # */
    # bool APDS9960_RPi::setProxGainCompEnable(uint8_t enable)
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from CONFIG3 register */
    # 	if( !wireReadDataByte(APDS9960_CONFIG3, val) ) {
    # 		return false;
    # 	}
    #
    # 	/* Set bits in register to given value */
    # 	enable &= 0b00000001;
    # 	enable = enable << 5;
    # 	val &= 0b11011111;
    # 	val |= enable;
    #
    # 	/* Write register value back into CONFIG3 register */
    # 	if( !wireWriteDataByte(APDS9960_CONFIG3, val) ) {
    # 		return false;
    # 	}
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Gets the current mask for enabled/disabled proximity photodiodes
    # *
    # * 1 = disabled, 0 = enabled
    # * Bit    Photodiode
    # *  3       UP
    # *  2       DOWN
    # *  1       LEFT
    # *  0       RIGHT
    # *
    # * @return Current proximity mask for photodiodes. 0xFF on error.
    # */
    # uint8_t APDS9960_RPi::getProxPhotoMask()
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from CONFIG3 register */
    # 	if( !wireReadDataByte(APDS9960_CONFIG3, val) ) {
    # 		return ERROR;
    # 	}
    #
    # 	/* Mask out photodiode enable mask bits */
    # 	val &= 0b00001111;
    #
    # 	return val;
    # }
    #
    # /**
    # * @brief Sets the mask for enabling/disabling proximity photodiodes
    # *
    # * 1 = disabled, 0 = enabled
    # * Bit    Photodiode
    # *  3       UP
    # *  2       DOWN
    # *  1       LEFT
    # *  0       RIGHT
    # *
    # * @param[in] mask 4-bit mask value
    # * @return True if operation successful. False otherwise.
    # */
    # bool APDS9960_RPi::setProxPhotoMask(uint8_t mask)
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from CONFIG3 register */
    # 	if( !wireReadDataByte(APDS9960_CONFIG3, val) ) {
    # 		return false;
    # 	}
    #
    # 	/* Set bits in register to given value */
    # 	mask &= 0b00001111;
    # 	val &= 0b11110000;
    # 	val |= mask;
    #
    # 	/* Write register value back into CONFIG3 register */
    # 	if( !wireWriteDataByte(APDS9960_CONFIG3, val) ) {
    # 		return false;
    # 	}
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Gets the entry proximity threshold for gesture sensing
    # *
    # * @return Current entry proximity threshold.
    # */
    # uint8_t APDS9960_RPi::getGestureEnterThresh()
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from GPENTH register */
    # 	if( !wireReadDataByte(APDS9960_GPENTH, val) ) {
    # 		val = 0;
    # 	}
    #
    # 	return val;
    # }
    #
    #
    # /**
    # * @brief Gets the low threshold for ambient light interrupts
    # *
    # * @param[out] threshold current low threshold stored on the APDS-9960
    # * @return True if operation successful. False otherwise.
    # */
    # bool APDS9960_RPi::getLightIntLowThreshold(uint16_t &threshold)
    # {
    # 	uint8_t val_byte;
    # 	threshold = 0;
    #
    # 	/* Read value from ambient light low threshold, low byte register */
    # 	if( !wireReadDataByte(APDS9960_AILTL, val_byte) ) {
    # 		return false;
    # 	}
    # 	threshold = val_byte;
    #
    # 	/* Read value from ambient light low threshold, high byte register */
    # 	if( !wireReadDataByte(APDS9960_AILTH, val_byte) ) {
    # 		return false;
    # 	}
    # 	threshold = threshold + ((uint16_t)val_byte << 8);
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Sets the low threshold for ambient light interrupts
    # *
    # * @param[in] threshold low threshold value for interrupt to trigger
    # * @return True if operation successful. False otherwise.
    # */
    # bool APDS9960_RPi::setLightIntLowThreshold(uint16_t threshold)
    # {
    # 	uint8_t val_low;
    # 	uint8_t val_high;
    #
    # 	/* Break 16-bit threshold into 2 8-bit values */
    # 	val_low = threshold & 0x00FF;
    # 	val_high = (threshold & 0xFF00) >> 8;
    #
    # 	/* Write low byte */
    # 	if( !wireWriteDataByte(APDS9960_AILTL, val_low) ) {
    # 		return false;
    # 	}
    #
    # 	/* Write high byte */
    # 	if( !wireWriteDataByte(APDS9960_AILTH, val_high) ) {
    # 		return false;
    # 	}
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Gets the high threshold for ambient light interrupts
    # *
    # * @param[out] threshold current low threshold stored on the APDS-9960
    # * @return True if operation successful. False otherwise.
    # */
    # bool APDS9960_RPi::getLightIntHighThreshold(uint16_t &threshold)
    # {
    # 	uint8_t val_byte;
    # 	threshold = 0;
    #
    # 	/* Read value from ambient light high threshold, low byte register */
    # 	if( !wireReadDataByte(APDS9960_AIHTL, val_byte) ) {
    # 		return false;
    # 	}
    # 	threshold = val_byte;
    #
    # 	/* Read value from ambient light high threshold, high byte register */
    # 	if( !wireReadDataByte(APDS9960_AIHTH, val_byte) ) {
    # 		return false;
    # 	}
    # 	threshold = threshold + ((uint16_t)val_byte << 8);
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Sets the high threshold for ambient light interrupts
    # *
    # * @param[in] threshold high threshold value for interrupt to trigger
    # * @return True if operation successful. False otherwise.
    # */
    # bool APDS9960_RPi::setLightIntHighThreshold(uint16_t threshold)
    # {
    # 	uint8_t val_low;
    # 	uint8_t val_high;
    #
    # 	/* Break 16-bit threshold into 2 8-bit values */
    # 	val_low = threshold & 0x00FF;
    # 	val_high = (threshold & 0xFF00) >> 8;
    #
    # 	/* Write low byte */
    # 	if( !wireWriteDataByte(APDS9960_AIHTL, val_low) ) {
    # 		return false;
    # 	}
    #
    # 	/* Write high byte */
    # 	if( !wireWriteDataByte(APDS9960_AIHTH, val_high) ) {
    # 		return false;
    # 	}
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Gets the low threshold for proximity interrupts
    # *
    # * @param[out] threshold current low threshold stored on the APDS-9960
    # * @return True if operation successful. False otherwise.
    # */
    # bool APDS9960_RPi::getProximityIntLowThreshold(uint8_t &threshold)
    # {
    # 	threshold = 0;
    #
    # 	/* Read value from proximity low threshold register */
    # 	if( !wireReadDataByte(APDS9960_PILT, threshold) ) {
    # 		return false;
    # 	}
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Sets the low threshold for proximity interrupts
    # *
    # * @param[in] threshold low threshold value for interrupt to trigger
    # * @return True if operation successful. False otherwise.
    # */
    # bool APDS9960_RPi::setProximityIntLowThreshold(uint8_t threshold)
    # {
    #
    # 	/* Write threshold value to register */
    # 	if( !wireWriteDataByte(APDS9960_PILT, threshold) ) {
    # 		return false;
    # 	}
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Gets the high threshold for proximity interrupts
    # *
    # * @param[out] threshold current low threshold stored on the APDS-9960
    # * @return True if operation successful. False otherwise.
    # */
    # bool APDS9960_RPi::getProximityIntHighThreshold(uint8_t &threshold)
    # {
    # 	threshold = 0;
    #
    # 	/* Read value from proximity low threshold register */
    # 	if( !wireReadDataByte(APDS9960_PIHT, threshold) ) {
    # 		return false;
    # 	}
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Sets the high threshold for proximity interrupts
    # *
    # * @param[in] threshold high threshold value for interrupt to trigger
    # * @return True if operation successful. False otherwise.
    # */
    # bool APDS9960_RPi::setProximityIntHighThreshold(uint8_t threshold)
    # {
    #
    # 	/* Write threshold value to register */
    # 	if( !wireWriteDataByte(APDS9960_PIHT, threshold) ) {
    # 		return false;
    # 	}
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Gets if ambient light interrupts are enabled or not
    # *
    # * @return 1 if interrupts are enabled, 0 if not. 0xFF on error.
    # */
    # uint8_t APDS9960_RPi::getAmbientLightIntEnable()
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from ENABLE register */
    # 	if( !wireReadDataByte(APDS9960_ENABLE, val) ) {
    # 		return ERROR;
    # 	}
    #
    # 	/* Shift and mask out AIEN bit */
    # 	val = (val >> 4) & 0b00000001;
    #
    # 	return val;
    # }
    #
    # /**
    # * @brief Turns ambient light interrupts on or off
    # *
    # * @param[in] enable 1 to enable interrupts, 0 to turn them off
    # * @return True if operation successful. False otherwise.
    # */
    # bool APDS9960_RPi::setAmbientLightIntEnable(uint8_t enable)
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from ENABLE register */
    # 	if( !wireReadDataByte(APDS9960_ENABLE, val) ) {
    # 		return false;
    # 	}
    #
    # 	/* Set bits in register to given value */
    # 	enable &= 0b00000001;
    # 	enable = enable << 4;
    # 	val &= 0b11101111;
    # 	val |= enable;
    #
    # 	/* Write register value back into ENABLE register */
    # 	if( !wireWriteDataByte(APDS9960_ENABLE, val) ) {
    # 		return false;
    # 	}
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Gets if proximity interrupts are enabled or not
    # *
    # * @return 1 if interrupts are enabled, 0 if not. 0xFF on error.
    # */
    # uint8_t APDS9960_RPi::getProximityIntEnable()
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from ENABLE register */
    # 	if( !wireReadDataByte(APDS9960_ENABLE, val) ) {
    # 		return ERROR;
    # 	}
    #
    # 	/* Shift and mask out PIEN bit */
    # 	val = (val >> 5) & 0b00000001;
    #
    # 	return val;
    # }
    #
    # /**
    # * @brief Turns proximity interrupts on or off
    # *
    # * @param[in] enable 1 to enable interrupts, 0 to turn them off
    # * @return True if operation successful. False otherwise.
    # */
    # bool APDS9960_RPi::setProximityIntEnable(uint8_t enable)
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from ENABLE register */
    # 	if( !wireReadDataByte(APDS9960_ENABLE, val) ) {
    # 		return false;
    # 	}
    #
    # 	/* Set bits in register to given value */
    # 	enable &= 0b00000001;
    # 	enable = enable << 5;
    # 	val &= 0b11011111;
    # 	val |= enable;
    #
    # 	/* Write register value back into ENABLE register */
    # 	if( !wireWriteDataByte(APDS9960_ENABLE, val) ) {
    # 		return false;
    # 	}
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Gets if gesture interrupts are enabled or not
    # *
    # * @return 1 if interrupts are enabled, 0 if not. 0xFF on error.
    # */
    # uint8_t APDS9960_RPi::getGestureIntEnable()
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from GCONF4 register */
    # 	if( !wireReadDataByte(APDS9960_GCONF4, val) ) {
    # 		return ERROR;
    # 	}
    #
    # 	/* Shift and mask out GIEN bit */
    # 	val = (val >> 1) & 0b00000001;
    #
    # 	return val;
    # }
    #
    # /**
    # * @brief Turns gesture-related interrupts on or off
    # *
    # * @param[in] enable 1 to enable interrupts, 0 to turn them off
    # * @return True if operation successful. False otherwise.
    # */
    # bool APDS9960_RPi::setGestureIntEnable(uint8_t enable)
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from GCONF4 register */
    # 	if( !wireReadDataByte(APDS9960_GCONF4, val) ) {
    # 		return false;
    # 	}
    #
    # 	/* Set bits in register to given value */
    # 	enable &= 0b00000001;
    # 	enable = enable << 1;
    # 	val &= 0b11111101;
    # 	val |= enable;
    #
    # 	/* Write register value back into GCONF4 register */
    # 	if( !wireWriteDataByte(APDS9960_GCONF4, val) ) {
    # 		return false;
    # 	}
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Clears the ambient light interrupt
    # *
    # * @return True if operation completed successfully. False otherwise.
    # */
    # bool APDS9960_RPi::clearAmbientLightInt()
    # {
    # 	uint8_t throwaway;
    # 	if( !wireReadDataByte(APDS9960_AICLEAR, throwaway) ) {
    # 		return false;
    # 	}
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Clears the proximity interrupt
    # *
    # * @return True if operation completed successfully. False otherwise.
    # */
    # bool APDS9960_RPi::clearProximityInt()
    # {
    # 	uint8_t throwaway;
    # 	if( !wireReadDataByte(APDS9960_PICLEAR, throwaway) ) {
    # 		return false;
    # 	}
    #
    # 	return true;
    # }
    #
    # /**
    # * @brief Tells if the gesture state machine is currently running
    # *
    # * @return 1 if gesture state machine is running, 0 if not. 0xFF on error.
    # */
    # uint8_t APDS9960_RPi::getGestureMode()
    # {
    # 	uint8_t val;
    #
    # 	/* Read value from GCONF4 register */
    # 	if( !wireReadDataByte(APDS9960_GCONF4, val) ) {
    # 		return ERROR;
    # 	}
    #
    # 	/* Mask out GMODE bit */
    # 	val &= 0b00000001;
    #
    # 	return val;
    # }#
