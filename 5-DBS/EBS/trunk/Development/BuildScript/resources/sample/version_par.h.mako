/***********************************************************************************
+------------------+
| SOFTWARE VERSION |
+------------------+
 X0000000000-0000
 ||||||||||| ||||
 ||||||||||| ||++-> release date(0~31)
 ||||||||||| |+---> release month(0~C)
 ||||||||||| +----> release year(0~9)
 |||||||||++------> diagnosis version(00~99)
 |||||||++--------> failsafe version(0A~9Z)
 |||||++----------> logic version(AA~ZZ)
 ||||+------------> system code2(A~Z)
 |||+-------------> system code1(1~4)
 |++--------------> vehicle(00~99)
 +----------------> proto

+----------------------+---+------------------+----------------------+
|    |  VEHICLE        |   |   SYSTEM code1   |   |  SYSTEM code2    |
|----+-----------------+---+------------------+---+------------------|
| 09 | HMC LC          | 1 | 2WD+no EBD       | A | ABS              |
| 10 | HMC FO          | 2 | 2WD+   EBD       | B | ABS+TDWS         |
| 11 | HMC SM          | 3 | 4WD+no EBD       | C | ABS+BTCS         |
| 12 | HMC SR          | 4 | 4WD+   EBD       | D | ABS+BTCS+TDWS    |
| 13 | HMC XD          +---+------------------+ E | ABS+FTCS         |
| 14 |                 |                      | F | ABS+FTCS+TDWS    |
| 15 | HPI DS-2        |                      | G | ABS+FTCS+VDC     |
| 20 | HMC FC          |                      | H | ABS+FTCS+VDC+TDWS|
| 21 | HMC GK          |                      | I | ABS+ETCS         |
| 43 | HMC SM          |                      |                      |   [2][16]
+----------------------+                      +----------------------+
***********************************************************************************/
#ifndef __VERSION_PAR
#define __VERSION_PAR

/*#pragma CONST_SEG SOFTWARE_VER*/

/***********************************************************************************/
    uint8_t MANDO_SW_Release_Counter = 1; 

    #if __CAR_MAKER == SSANGYONG
        uint32_t SYMC_SW_Release_Counter = 0x164401;
    #endif

    #if M_HKMC_SW_ID_STANDARD == ENABLE
        uint8_t ELECTRIC_SW_DLS[4] = {"A.00"};
    #else
        uint8_t ELECTRIC_SW_DLS[1] = {"A"};
    #endif

    #if __ECU==ABS_ECU_1
        const uint8_t VERSION[2][16] = {"NF ABS          ",
                                        "${Car_Par[folder[count]]['REVISION']}"};
    #elif __ECU==ESP_ECU_1
        const uint8_t VERSION[2][16] = {"TL ESC          ",
                                        "${Car_Par[folder[count]]['REVISION']}"};
    #endif

/*#pragma CONST_SEG DEFAULT*/

#endif /* __VERSION_PAR */
