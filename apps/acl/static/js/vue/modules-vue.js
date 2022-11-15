new Vue({
    delimiters: ['[[', ']]'],
    el:'#appModules',
    data:{
        formPerm:{},
        formMenu:{},
        role:[],
        access:[],
        menu:[],
        submenu:[],
        errors: [],
        index_module:'',
        state_form:'create',
        state_formmenu:'create',
        name_menu:'',
        pk_menu:''
    },
    created: function () {
        this.listAccess();
        this.listMenu();
    },

    methods:{

        listAccess(){
            const self = this
            axios.get('access/', {})
            .then(function (response) {
                if (response.data.length > 0) {
                    self.access = response.data
                }
            });
        },
        listMenu(){
            const self = this
            axios.get('menu/', {})
            .then(function (response) {
                if (response.data.length > 0) {
                    self.menu = response.data
                    setTimeout(() => $('.show-tick').selectpicker('refresh'));
                }
            });
        },
        changeStateC:function(){
            this.state_form = 'create';
            this.formPerm = {};
        },
        sendModule:function(e){
            if(this.state_form == 'create'){
                this.createModule(e);
            }else{
                this.updateModule(e);
            }
        },
        createModule:function(e){
            const self = this
            var name_module = $('#name_module').val();
            var app = $('#app').val();
            var acl = $('#acl').val();

            if(app && acl && name_module){
                var csrfmiddlewaretoken = $("[name=csrfmiddlewaretoken]").val();
                var bodyFormData = new FormData(e.target);
                    axios({
                        headers: { 'X-CSRFToken': csrfmiddlewaretoken,'Content-Type': 'multipart/form-data' },
                        method: 'POST',
                        url: 'access/',
                        data: bodyFormData,
                       
                    }).then(response => {
                        if (response.data.length > 0){
                            self.access.push(response.data[0])
                            self.formPerm = {}
                            toastr.success('Módulo creado correctamente '+ response.data[0].fields.name + ' con ruta ' + response.data[0].fields.codename, null, { "closeButton": false });                            
                            $("#ModalModule").modal('hide');
                            setTimeout(() => $('.show-tick').selectpicker('refresh'));
                        }
                        else{
                            toastr.warning('Ya existe el módulo', null, { "closeButton": false });                            
                        }
                       
                    }).catch(e => {
                        self.errors.push(e)
                    })
            }
            else{
                toastr.error('¡No es posible guardar!', null, { "closeButton": false });                            
            }
        
        },
        editModule:function(_params, pk, index){
            this.state_form = 'edit';
            this.formPerm.app = _params.content_type;
            this.formPerm.acl = _params.codename;
            this.formPerm.name_module = _params.name;
            this.formPerm.pk = pk
            this.index_module = index;
            setTimeout(() => $('.show-tick').selectpicker('refresh'));
        },
        updateModule:function(e){
            const self = this
            var name_module = $('#name_module').val();
            var app = $('#app').val();
            var acl = $('#acl').val();
         
            if(app && acl && name_module){
                var csrfmiddlewaretoken = $("[name=csrfmiddlewaretoken]").val();
                var bodyFormData = new FormData(e.target);
                    axios({
                        headers: { 'X-CSRFToken': csrfmiddlewaretoken,'Content-Type': 'multipart/form-data' },
                        method: 'PUT',
                        url: 'access/',
                        data: bodyFormData,
                       
                    }).then(response => {
                            self.access[self.index_module] = response.data[0]
                            setTimeout(() => $('.show-tick').selectpicker('refresh'));
                            toastr.success('Módulo actualizado correctamente '+ response.data[0].fields.name + ' con ruta ' + response.data[0].fields.codename, null, { "closeButton": false });                            
                            $("#ModalModule").modal('hide');
                            self.formPerm = {};
                            self.state_form = 'create';
                       
                    }).catch(e => {
                        self.errors.push(e)
                    })
            }
            else{
                toastr.error('¡No es posible guardar!', null, { "closeButton": false });                            

            }
        
        },
        deleteModule(detail, index){
            const self = this
            swal({
                title: "Desea Eliminar " + detail.fields.name +" ?",
                text: "¡No podrás recuperar este Elemento!!",
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: "#DD6B55",
                confirmButtonText: "Si, Eliminar!",
                cancelButtonText: "No, Cancelar!",
                closeOnConfirm: false,
                closeOnCancel: false
            },
            function (isConfirm) {
                if (isConfirm) {
                    var csrfmiddlewaretoken = $("[name=csrfmiddlewaretoken]").val();
							axios({
								headers: { 'X-CSRFToken': csrfmiddlewaretoken },
								method: 'delete',
								url: 'access/',
								data: {
									pk:detail.pk,
								}
							}).then(function (response) {
                                if (response.status == 200) {
                                    self.access.splice(index, 1);
                                    swal({
                                        title: "Eliminado!",
                                        text: "El elemento se elimino correctamente",
                                        type: "success",
                                        timer: 1200,
                                        showConfirmButton: false
                                    });
                                }

                            }).catch(e => {
                                self.errors.push(e)
                            }) 
                }
                else{
                    swal({
                        title: "Cancelado!",
                        text: "Tu elemento esta seguro",
                        type: "error",
                        timer: 1200,
                        showConfirmButton: false
                    });  
                }
            })
         
        },
        gestionMenu:function(_params, pk){
            this.state_formmenu = 'create';
            this.formMenu = {}
            this.formMenu.app = _params.content_type;
            this.formMenu.menu = _params.menu;
            this.name_menu = _params.name
            this.pk_menu = _params.menu;
            this.listSubMenu(_params.menu)
            setTimeout(() => $('.show-tick').selectpicker('refresh'));
        },
        listSubMenu(menu){
            const self = this;
            self.submenu = [];
            axios.get('submenu/', { params: {menu : menu }})
            .then(function (response) {
                if (response.data.length > 0) {
                    self.submenu = response.data
                    setTimeout(() => $('.show-tick').selectpicker('refresh'));
                }
            });
        },
        createMenu:function(){
            this.state_formmenu = 'create';
            this.formMenu.ordensub = '';
            this.formMenu.submenu = '';
            this.formMenu.acl = '';
            this.formMenu.pk = ''
            setTimeout(() => $('.show-tick').selectpicker('refresh'));
        },
        editMenu:function(_params, pk){
            this.formMenu = {}
            this.state_formmenu = 'edit';
            this.formMenu.submenu = _params.submenus.fields.name;
            this.formMenu.acl = _params.submenus.fields.codename;
            this.formMenu.ordensub = _params.fields.order;
            this.formMenu.app = _params.submenus.fields.content_type;
            this.formMenu.menu = _params.fields.menu[0];
            this.formMenu.pk = _params.pk
            // this.formMenu = {}
            setTimeout(() => $('.show-tick').selectpicker('refresh'));
        },
        sendSubMenu:function(e){
            if(this.state_formmenu == 'create'){
                this.createSubMenu(e);
            }else{
                this.updateSubMenu(e);
            }
        },
        createSubMenu:function(e){
            const self = this
            var app = $('#appsb').val();
            var acl = $('#aclsb').val();
            var menu = $('#menusb').val();
            var submenu = $('#submenusb').val();
         
            if(app && acl && menu && submenu){
                var csrfmiddlewaretoken = $("[name=csrfmiddlewaretoken]").val();
                var bodyFormData = new FormData(e.target);
                    axios({
                        headers: { 'X-CSRFToken': csrfmiddlewaretoken,'Content-Type': 'multipart/form-data' },
                        method: 'POST',
                        url: 'submenu/',
                        data: bodyFormData,
                       
                    }).then(response => {
                        if (response.data.length > 0){
                            self.submenu = []
                            self.formMenu.submenu = '';
                            self.formMenu.acl = '';
                            self.formMenu.name_module = '';
                            self.formMenu.ordensub = '';
                            self.listSubMenu(menu)
                            toastr.success('Sub menú creado correctamente.', null, { "closeButton": false });                            
                            setTimeout(() => $('.show-tick').selectpicker('refresh'));
                            $("#ModalModule").modal('hide');
                        }
                        else{
                            toastr.warning('Ya existe el módulo', null, { "closeButton": false });                            
                        }
                       
                    }).catch(e => {
                        self.errors.push(e)
                    })
            }
            else{
                toastr.error('¡No es posible guardar!', null, { "closeButton": false });                            

            }
        
        },
        updateSubMenu:function(e){
            const self = this
            var app = $('#appsb').val();
            var acl = $('#aclsb').val();
            var menu = $('#menusb').val();
            var submenu = $('#submenusb').val();
         
            if(app && acl && menu && submenu){
                var csrfmiddlewaretoken = $("[name=csrfmiddlewaretoken]").val();
                var bodyFormData = new FormData(e.target);
                    axios({
                        headers: { 'X-CSRFToken': csrfmiddlewaretoken,'Content-Type': 'multipart/form-data' },
                        method: 'PUT',
                        url: 'submenu/',
                        data: bodyFormData,
                       
                    }).then(response => {
                        if (response.data.length > 0){
                            self.submenu = []
                            self.listSubMenu(menu)
                            self.createMenu()
                            toastr.success('Sub menú actualizado correctamente.', null, { "closeButton": false });                            
                            setTimeout(() => $('.show-tick').selectpicker('refresh'));
                            $("#ModalModule").modal('hide');
                        }
                        else{
                            toastr.warning('Ya existe el módulo', null, { "closeButton": false });                            
                        }
                       
                    }).catch(e => {
                        self.errors.push(e)
                    })
            }
            else{
                toastr.error('¡No es posible guardar!', null, { "closeButton": false });                            

            }
        
        },
        deleteMenu(detail, index){
            const self = this
            swal({
                title: "Desea Eliminar " + detail.submenus.fields.name +" ?",
                text: "¡No podrás recuperar este Elemento!!",
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: "#DD6B55",
                confirmButtonText: "Si, Eliminar!",
                cancelButtonText: "No, Cancelar!",
                closeOnConfirm: false,
                closeOnCancel: false
            },
            function (isConfirm) {
                if (isConfirm) {
                    var csrfmiddlewaretoken = $("[name=csrfmiddlewaretoken]").val();
							axios({
								headers: { 'X-CSRFToken': csrfmiddlewaretoken },
								method: 'delete',
								url: 'submenu/',
								data: {
									pk:detail.pk,
								}
							}).then(function (response) {
                                if (response.status == 200) {
                                    self.submenu.splice(index, 1);
                                    swal({
                                        title: "Eliminado!",
                                        text: "El elemento se elimino correctamente",
                                        type: "success",
                                        timer: 1200,
                                        showConfirmButton: false
                                    });
                                }

                            }).catch(e => {
                                self.errors.push(e)
                            }) 
                }
                else{
                    swal({
                        title: "Cancelado!",
                        text: "Tu elemento esta seguro",
                        type: "error",
                        timer: 1200,
                        showConfirmButton: false
                    });  
                }
            })
         
        },
        sendOrderSubMenus:function(){
            let csrfmiddlewaretoken = $("[name=csrfmiddlewaretoken]").val();
            let dictplacestage = $("[name=order_menu]").val();
            const self = this;
            axios({
                headers: {  
                    'X-CSRFToken': csrfmiddlewaretoken
                },
                method:'POST',
                url:'ordersubmenu/',
                data: dictplacestage

                }).then(response =>{
                    toastr.success('Orden guardado correctamente', null, { "closeButton": true });
                    self.listSubMenu(self.pk_menu);
                    self.createMenu()
                }).catch(e => {
                    this.errors.push(e)
                })
        },
    },
})