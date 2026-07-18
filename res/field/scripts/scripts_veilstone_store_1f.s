#include "macros/scrcmd.inc"
#include "res/text/bank/veilstone_store_1f.h"

#define LOCAL_VAR_ACCESSORY_ID VAR_0x8004
#define LOCAL_VAR_COUNT        VAR_0x8005
#define LOCAL_VAR_OUTFIT       VAR_0x8006
#define LOCAL_VAR_OUTFIT_FLAG  VAR_0x8007
#define LOCAL_VAR_OWNED        VAR_0x8008

#define OUTFIT_PRICE 3000

    ScriptEntry VeilstoneStore1F_Attendant
    ScriptEntry VeilstoneStore1F_MiddleAgedMan
    ScriptEntry VeilstoneStore1F_Lady
    ScriptEntry VeilstoneStore1F_RightVendor
    ScriptEntry VeilstoneStore1F_LeftVendor
    ScriptEntry VeilstoneStore1F_BgSign
    ScriptEntry VeilstoneStore1F_Directory
    ScriptEntry VeilstoneStore1F_Socialite
    ScriptEntry VeilstoneStore1F_Stylist
    ScriptEntryEnd

VeilstoneStore1F_Attendant:
    NPCMessage VeilstoneStore1F_Text_Welcome
    End

VeilstoneStore1F_MiddleAgedMan:
    NPCMessage VeilstoneStore1F_Text_EnsureCustomerSatisfaction
    End

VeilstoneStore1F_Lady:
    NPCMessage VeilstoneStore1F_Text_FormalAirOfLuxury
    End

VeilstoneStore1F_RightVendor:
    PokeMartSpecialtiesWithGreeting MART_SPECIALTIES_ID_VEILSTONE_1F_RIGHT
    End

VeilstoneStore1F_LeftVendor:
    PokeMartSpecialtiesWithGreeting MART_SPECIALTIES_ID_VEILSTONE_1F_LEFT
    End

VeilstoneStore1F_BgSign:
    EventMessage VeilstoneStore1F_Text_DiscoverANewYou
    End

VeilstoneStore1F_Directory:
    EventMessage VeilstoneStore1F_Text_Directory
    End

VeilstoneStore1F_Socialite:
    PlaySE SEQ_SE_CONFIRM
    LockAll
    FacePlayer
    GoToIfSet FLAG_RECEIVED_VEILSTONE_STORE_1F_ACCESSORY_STARTER_MASK, VeilstoneStore1F_Socialite_AfterMaskGiven
    GetPlayerStarterSpecies VAR_RESULT
    CallIfEq VAR_RESULT, SPECIES_TURTWIG, VeilstoneStore1F_Socialite_Turtwig
    CallIfEq VAR_RESULT, SPECIES_CHIMCHAR, VeilstoneStore1F_Socialite_Chimchar
    CallIfEq VAR_RESULT, SPECIES_PIPLUP, VeilstoneStore1F_Socialite_Piplup
    SetVar VAR_VEILSTONE_STORE_1F_ACCESSORY_STARTER_MASK, LOCAL_VAR_ACCESSORY_ID
    BufferAccessoryNameWithArticle 0, LOCAL_VAR_ACCESSORY_ID
    Message VeilstoneStore1F_Text_IMadeAnAccessory
    SetVar LOCAL_VAR_COUNT, 1
    Common_GiveAccessoryWaitForConfirm
    SetFlag FLAG_RECEIVED_VEILSTONE_STORE_1F_ACCESSORY_STARTER_MASK
    CloseMessage
    ReleaseAll
    End

VeilstoneStore1F_Socialite_AfterMaskGiven:
    BufferAccessoryName 0, VAR_VEILSTONE_STORE_1F_ACCESSORY_STARTER_MASK
    Message VeilstoneStore1F_Text_DifferentLookForContests
    WaitButton
    CloseMessage
    ReleaseAll
    End

VeilstoneStore1F_Socialite_Turtwig:
    SetVar LOCAL_VAR_ACCESSORY_ID, ACCESSORY_PIPLUP_MASK
    Return

VeilstoneStore1F_Socialite_Chimchar:
    SetVar LOCAL_VAR_ACCESSORY_ID, ACCESSORY_TURTWIG_MASK
    Return

VeilstoneStore1F_Socialite_Piplup:
    SetVar LOCAL_VAR_ACCESSORY_ID, ACCESSORY_CHIMCHAR_MASK
    Return

VeilstoneStore1F_Stylist:
    PlaySE SEQ_SE_CONFIRM
    LockAll
    FacePlayer
    ShowMoney 20, 2
    Message VeilstoneStore1F_Text_StylistDiscoverANewYou
    WaitButton
    Message VeilstoneStore1F_Text_StylistWhichOutfit

VeilstoneStore1F_Stylist_Menu:
    InitLocalTextMenu 1, 1, 0, VAR_RESULT, TRUE
    AddMenuEntryImm VeilstoneStore1F_Text_OutfitOriginal, 0
    AddMenuEntryImm VeilstoneStore1F_Text_OutfitRed, 1
    AddMenuEntryImm VeilstoneStore1F_Text_OutfitGreen, 2
    AddMenuEntryImm VeilstoneStore1F_Text_OutfitPurple, 3
    AddMenuEntryImm VeilstoneStore1F_Text_OutfitOrange, 4
    AddMenuEntryImm VeilstoneStore1F_Text_OutfitGrey, 5
    AddMenuEntryImm VeilstoneStore1F_Text_OutfitCancel, 6
    ShowMenu
    GoToIfGe VAR_RESULT, 6, VeilstoneStore1F_Stylist_MaybeNextTime
    SetVar LOCAL_VAR_OUTFIT, VAR_RESULT
    GoToIfEq LOCAL_VAR_OUTFIT, 0, VeilstoneStore1F_Stylist_AlreadyOwned
    SetVar LOCAL_VAR_OUTFIT_FLAG, FLAG_OUTFIT_OWNED_0
    AddVar LOCAL_VAR_OUTFIT_FLAG, LOCAL_VAR_OUTFIT
    CheckFlagFromVar LOCAL_VAR_OUTFIT_FLAG, LOCAL_VAR_OWNED
    GoToIfEq LOCAL_VAR_OWNED, TRUE, VeilstoneStore1F_Stylist_AlreadyOwned
    Message VeilstoneStore1F_Text_StylistThatOneIs
    ShowYesNoMenu VAR_RESULT
    GoToIfNe VAR_RESULT, MENU_YES, VeilstoneStore1F_Stylist_MaybeNextTime
    GoToIfNotEnoughMoney OUTFIT_PRICE, VeilstoneStore1F_Stylist_NotEnoughMoney
    AddToGameRecord RECORD_MONEY_SPENT, OUTFIT_PRICE
    RemoveMoney2 OUTFIT_PRICE
    UpdateMoneyDisplay
    PlaySE SEQ_SE_DP_REGI
    WaitSE SEQ_SE_DP_REGI
    SetFlagFromVar LOCAL_VAR_OUTFIT_FLAG
    Message VeilstoneStore1F_Text_StylistLooksWonderful
    GoTo VeilstoneStore1F_Stylist_Wear

VeilstoneStore1F_Stylist_AlreadyOwned:
    Message VeilstoneStore1F_Text_StylistChangedIntoIt

VeilstoneStore1F_Stylist_Wear:
    SetPlayerOutfit LOCAL_VAR_OUTFIT
    WaitButton
    CloseMessage
    HideMoney
    ReleaseAll
    End

VeilstoneStore1F_Stylist_NotEnoughMoney:
    Message VeilstoneStore1F_Text_StylistNotEnoughMoney
    WaitButton
    CloseMessage
    HideMoney
    ReleaseAll
    End

VeilstoneStore1F_Stylist_MaybeNextTime:
    Message VeilstoneStore1F_Text_StylistMaybeNextTime
    WaitButton
    CloseMessage
    HideMoney
    ReleaseAll
    End

    .balign 4, 0
