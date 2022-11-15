$(function () {
    $('.colorpicker').colorpicker();   

    //Masked Input ============================================================================================================================
    //Date
    $('.date').inputmask('yyyy-mm-dd', { placeholder: '____/__/__' });

    //Time
    $('.time12').inputmask('hh:mm t', { placeholder: '__:__ _m', alias: 'time12', hourFormat: '12' });
    $('.time24').inputmask('hh:mm', { placeholder: '__:__ _m', alias: 'time24', hourFormat: '24' });

    //Date Time
    $('.datetime').inputmask('d/m/y h:s', { placeholder: '__/__/____ __:__', alias: "datetime", hourFormat: '24' });

    //Mobile Phone Number
    $('.mobile-phone-number').inputmask('+99 (999) 999-99-99', { placeholder: '+__ (___) ___-__-__' });
    //Phone Number
    $('.phone-number').inputmask('+99 (999) 999-99-99', { placeholder: '+__ (___) ___-__-__' });

    //Dollar Money
    $('.money-dollar').inputmask('99,99 $', { placeholder: '__,__ $' });
   
    //IP Address
    $('.ip').inputmask('999.999.999.999', { placeholder: '___.___.___.___' });

    //Credit Card
    $('.credit-card').inputmask('9999 9999 9999 9999', { placeholder: '____ ____ ____ ____' });

    //Email
    $('.email').inputmask({ alias: "email" });

    //Serial Key
    $('.key').inputmask('****-****-****-****', { placeholder: '____-____-____-____' });
    //===========================================================================================================================================

    //Multi-select
    $('#optgroup').multiSelect({ selectableOptgroup: true });

});