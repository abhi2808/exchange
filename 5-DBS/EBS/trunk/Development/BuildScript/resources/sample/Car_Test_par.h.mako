/*
*******************************************************************************
+------------------------------------------------------------------------------
| Directory Par
| Filename  car_test_par.h
| Project   MGH100 INTERNATIONAL
+------------------------------------------------------------------------------
*******************************************************************************
=> Revision Note
-------------------------------------------------------------------------------
*******************************************************************************
*/
/* CAN Logging */
#define __LOGGER
#if defined(__LOGGER)

#define M_LOGGER_DATA_TYPE       M_LOGGER_CTRL

  /*  M_LOGGER_CTRL
  M_LOGGER_CAN
  M_LOGGER_FS
  M_LOGGER_VD
  M_LOGGER_PF
  M_LOGGER_DIAG
  M_LOGGER_PBC  */

#define ESC_LOG_TX_MAIN_5MS							DISABLE /* Disable: 10ms*10msg , Enable: 5ms*4msg + 10ms*2msg */
#define ESC_LOG_TX_SUB_5MS							DISABLE /* Disable: 10ms*10msg , Enable: 5ms*4msg + 10ms*2msg */
#define VIEW_SET_USING_DIAG							ENABLE

#if ((__ECU == ABS_ECU_1) || (__CAR_MAKER == GEELY) || (__CAR_MAKER == GM_CHINA) || (__CAR_MAKER == BA) ||(__CAR_MAKER == SEM) || (__CAR_MAKER == IKCO))
#define SUB_LOG_MSG_ENABLE                          DISABLE /* ABS/GEELY : 1 channel only */
#else
#define SUB_LOG_MSG_ENABLE                          ENABLE /* Sub-CAN channel mounted vehicle only */
#endif

#endif

/* VX1000 XCP */
#define M_XCP_ENABLE					${Car_Test_Par[folder[count]]['M_XCP_ENABLE']}

/* VX1000 Online Calibration */
#if (M_XCP_ENABLE == ENABLE)
	#define M_XCP_ONLINE_CAL_ENABLE		${Car_Test_Par[folder[count]]['M_XCP_ONLINE_CAL_ENABLE']}

  #if (M_XCP_ONLINE_CAL_ENABLE == ENABLE)

	#if ((__CAR_MAKER == GM_KOREA)||(__CAR_MAKER == GM_USA)||(__CAR_MAKER == GM_CHINA))
	#define M_XCP_ONLINE_CAL_VRNT					DISABLE	/* Always DISABLE */
	#else
	#define M_XCP_ONLINE_CAL_VRNT					DISABLE
	#endif
	  
	#if (M_XCP_ONLINE_CAL_VRNT == ENABLE)
	  
	/* Must ENABLE M_XCP_ONLINE_CAL_DRV or M_XCP_ONLINE_CAL_SPRTS */
	#define M_XCP_ONLINE_CAL_DRV					DISABLE	/* Using manual 4WD mode */
	#define M_XCP_ONLINE_CAL_SPRTS					DISABLE	/* Using sports mode */
	
	/* Do not set 1, 23, 24 */
	#define M_XCP_ONLINE_CAL_BRK_NORM				2 /* Normal mode set */
	#define M_XCP_ONLINE_CAL_BRK_NOT_NORM			3 /* Not normal mode set (AWD or Sprts) */
	
	/* Do not set 1, 47, 48 */
	#define M_XCP_ONLINE_CAL_ENG_NORM				2 /* Normal mode set */
	#define M_XCP_ONLINE_CAL_ENG_NOT_NORM			3 /* Not normal mode set (AWD or Sprts) */
	
	#endif
  #endif
#endif

