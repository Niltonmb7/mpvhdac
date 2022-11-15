new Vue({
    delimiters: ['[[', ']]'],
    el:'#appRoles',
    data:{
        formRole:{},
        formAccess:{
            access:'',
            roles:[],
        },

        role:[],
        access:[],
        errors: [],

        rol_pk:'',
        rol_name:''
    },
    created: function () {
        this.listRole();
        this.listAccess();
    },

    methods:{
        listRole(){
            const self = this
            axios.get('role/', {})
            .then(function (response) {
                if (response.data.length > 0) {
                    self.role = response.data
                }
            });
        },

        listAccess(){
            const self = this
            axios.get('access/', {})
            .then(function (response) {
                if (response.data.length > 0) {
                    self.access = response.data
                    setTimeout(() => $('.show-tick').selectpicker('refresh'));
                }
            });
        },
     
        sendRole:function(e){
            var pk_role = $('#pk_role').val();
            var csrfmiddlewaretoken = $("[name=csrfmiddlewaretoken]").val();
            var bodyFormData = new FormData(e.target);
                axios({
                    headers: { 'X-CSRFToken': csrfmiddlewaretoken,'Content-Type': 'multipart/form-data' },
                    method: 'POST',
                    url: 'role/',
                    data: bodyFormData,
                   
                }).then(response => {
                    if (response.data.length > 0){
                        if(pk_role){
                            this.role[this.index_rol] = response.data[0];
                            toastr.success('Rol actualizado correctamente', null, { "closeButton": false });
                        }
                        else{
                            this.role.push(response.data[0])
                            toastr.success('Rol creado correctamente', null, { "closeButton": false });
                        }
                        
                        this.formRole = {}
                        $("#ModalRol").modal('hide');

                    }
                   
                }).catch(e => {
                    this.errors.push(e)
                })
        },
        editRole:function(_name, pk, index){
            this.formRole = {}
            this.formRole.pk = pk;
            this.formRole.name = _name;
            this.index_rol = index;
            setTimeout(() => $('.show-tick').selectpicker('refresh'));
        },
        deleteRole(detail, index){
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
								url: 'role/',
								data: {
									pk:detail.pk,
								}
							}).then(function (response) {
                                if (response.status == 200) {
                                    self.role.splice(index, 1);
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
        openModalPermiso:function(pk, name){
            this.rol_pk = pk;
            this.rol_name = name;
        },
        sendRolePermission:function(e){
            const self = this
            var access = $('#access').val();
            var roles = this.rol_pk
            
            if(access && roles){
                var csrfmiddlewaretoken = $("[name=csrfmiddlewaretoken]").val();
                var bodyFormData = new FormData(e.target);
                bodyFormData.set('roles', this.rol_pk);
                    axios({
                        headers: { 'X-CSRFToken': csrfmiddlewaretoken,'Content-Type': 'multipart/form-data' },
                        method: 'POST',
                        url: 'rolepermission/',
                        data: bodyFormData,
                       
                    }).then(response => {
                        if (response.data.length > 0){
                             $.each(response.data, function (index, value) {
                                     indice =  self.role.findIndex(function(rol) {
                                            return rol.pk == value.pk;
                                        });

                                    self.role[indice].fields.permisos.push(value.fields.permisos[0])
                                    toastr.success('¡Permiso agregado! ' + 'al Rol ' + value.fields.name + ' con permiso: ' + value.fields.permisos[0].fields.name, null, { "closeButton": false });                            
                           
                                });
                            $("#ModalPermiso").modal('hide');                           
                            self.formAccess = {
                                access:'',
                                roles:[],
                            }
                        }
                        else{
                            $.toast({
                                heading: '¡No se puede agregar accesos!',
                                text: 'todos los roles ya cuentas con accesos',
                                position: 'top-right',
                                loaderBg:'#f57e03',
                                icon: 'warning',
                                hideAfter: 3000, 
                                stack: 6
                            });
                        }
                       
                    }).catch(e => {
                        self.errors.push(e)
                    })
            }
            else{
                toastr.error('¡No es posible guardar!', null, { "closeButton": false });                            
            }
        
        },
        deleteRolePermission(detailp,detailg, indexp,indexg){
            const self = this
            swal({
                title: "Desea Eliminar " + detailp.fields.name +" ?",
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
								url: 'rolepermission/',
								data: {
									pk_rol:detailg.pk,
									pk_perm:detailp.pk,
								}
							}).then(function (response) {
                                if (response.status == 200) {
                                    self.role[indexg].fields.permisos.splice(indexp, 1);
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

    },
})