#ifndef __CAR_PAR_H
#define __CAR_PAR_H

/* if enabled, you can change from legacy to autosar mode */
#define __AUTOSAR_CORE_ENA
/*#define __AUTOSAR_HEADER_ARCH_ENA*/

#if defined(__AUTOSAR_HEADER_ARCH_ENA)
	#include "Mstatic_autosar.h"
#endif

#include "Car_Def.h"

/* CAR Definiton */
#define __CAR_MAKER                 ${Car_Par[folder[count]]['__CAR_MAKER']}  
#define __CAR                       ${Car_Par[folder[count]]['__CAR']}


/* ECU selection */
#if (V_ECU == 1)
#define __ECU                       ABS_ECU_1
#elif (V_ECU == 2)
#define __ECU                       ESP_ECU_1
#endif

/* ECU DV LEVEL */
#define MGH100_ECU_DV_LEVEL      	${Car_Par[folder[count]]['MGH100_ECU_DV_LEVEL']}

/* MOCi selection */
#if (V_MOCI == 0)
#define __MGH100_MOCi				DISABLE
#elif (V_MOCI == 1)
#define __MGH100_MOCi				ENABLE
#endif

/*Car Varinat Number*/
#define CAR_VAR_NUM                 ${Car_Par[folder[count]]['CAR_VAR_NUM']}

/*Car Calibration Varinat Number*/
#define CAR_CAL_NUM                 ${Car_Par[folder[count]]['CAR_CAL_NUM']}
#define	CAR_FCT_CAL_NUM				${Car_Par[folder[count]]['CAR_FCT_CAL_NUM']}
#define	CAR_DIAG_CAL_NUM			${Car_Par[folder[count]]['CAR_DIAG_CAL_NUM']}

/* Region selection */
#define REGION_TYPE           		${Car_Par[folder[count]]['REGION_TYPE']}

#if (__MGH100_MOCi == ENABLE)
    /* EPB System selection */
    #define __ECU_TYPE				MOC
#endif

#define __IDB_SYSTEM				${Car_Par[folder[count]]['__IDB_SYSTEM']}

/* Library management */
#define GEN_SINGLE_LIB_ENABLE 		DISABLE
#define GEN_LIB_FOR_MODULE

/* ESC REGEN */
#define MGH100_ESC_REGEN 			${Car_Par[folder[count]]['MGH100_ESC_REGEN']}
/* Moci REGEN */
#define MGH100_MOCI_REGEN 			${Car_Par[folder[count]]['MGH100_MOCI_REGEN']}
#if MGH100_ESC_REGEN==ENABLE && MGH100_MOCI_REGEN==ENABLE
    #error "Wrong Car_par.h: Both of MGH100_ESC_REGEN&MGH100_MOCI_REGEN are enabled"
#endif
#define USE_MGH100BSG_DEV           ${Car_Par[folder[count]]['USE_MGH100BSG_DEV']}

/* ABS-Large */
#define MGH100_ABS_LARGE 			${Car_Par[folder[count]]['MGH100_ABS_LARGE']}

/* Test Mode selection */
#define __TEST_MODE_ENABLE          ${Car_Par[folder[count]]['__TEST_MODE_ENABLE']}
#if __TEST_MODE_ENABLE == ENABLE
    #include "Car_Test_par.h"
#endif

#include "Car_Sel_par.h"

#endif
