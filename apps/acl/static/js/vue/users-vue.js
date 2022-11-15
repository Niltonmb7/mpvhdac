new Vue({
    delimiters: ['[[', ']]'],
    el:'#appUsers',
    data:{
        formRole:{},
        formusers:{
            users:'',
            roles:[],
        },

        roles:[],
        users:[],
        errors: [],

        rol_pk:'',
        rol_name:'',

        form:{}
    },
    created: function () {
        this.listUsers();
        this.footable();
    },

    methods:{
        footable(){
            $(window).on('load', function() {

                // Row Toggler
                // -----------------------------------------------------------------
                $('#demo-foo-row-toggler').footable();
            
                // Accordion
                // -----------------------------------------------------------------
                $('#demo-foo-accordion').footable().on('footable_row_expanded', function(e) {
                    $('#demo-foo-accordion tbody tr.footable-detail-show').not(e.row).each(function() {
                        $('#demo-foo-accordion').data('footable').toggleDetail(this);
                    });
                });
            
                // Pagination
                // -----------------------------------------------------------------
                $('#demo-foo-pagination').footable();
                $('#demo-show-entries').change(function (e) {
                    e.preventDefault();
                    var pageSize = $(this).val();
                    $('#demo-foo-pagination').data('page-size', pageSize);
                    $('#demo-foo-pagination').trigger('footable_initialized');
                });
            
                // Filtering
                // -----------------------------------------------------------------
                var filtering = $('#demo-foo-filtering');
                filtering.footable().on('footable_filtering', function (e) {
                    var selected = $('#demo-foo-filter-status').find(':selected').val();
                    e.filter += (e.filter && e.filter.length > 0) ? ' ' + selected : selected;
                    e.clear = !e.filter;
                });
            
                // Filter status
                $('#demo-foo-filter-status').change(function (e) {
                    e.preventDefault();
                    filtering.trigger('footable_filter', {filter: $(this).val()});
                });
            
                // Search input
                $('#demo-foo-search').on('input', function (e) {
                    e.preventDefault();
                    filtering.trigger('footable_filter', {filter: $(this).val()});
                });
            
            
                
            
                // Search input
                $('#demo-input-search2').on('input', function (e) {
                    e.preventDefault();
                    addrow.trigger('footable_filter', {filter: $(this).val()});
                });
                
                // Add & Remove Row
                var addrow = $('#demo-foo-addrow');
                addrow.footable().on('click', '.delete-row-btn', function() {
            
                    //get the footable object
                    var footable = addrow.data('footable');
            
                    //get the row we are wanting to delete
                    var row = $(this).parents('tr:first');
            
                    //delete the row
                    footable.removeRow(row);
                });
                var addrow = $('#demo-foo-addrow2');
                addrow.footable().on('click', '.delete-row-btn', function() {
            
                    //get the footable object
                    var footable = addrow.data('footable');
            
                    //get the row we are wanting to delete
                    var row = $(this).parents('tr:first');
            
                    //delete the row
                    footable.removeRow(row);
                });
                // Add Row Button
                // $('#demo-btn-addrow').click(function() {
            
                //     //get the footable object
                //     var footable = addrow.data('footable');
                    
                //     //build up the row we are wanting to add
                //     var newRow = '<tr><td>thome</td><td>Woldt</td><td>Airline Transport Pilot</td><td>3 Oct 2016</td><td><span class="label label-table label-success">Active</span></td><td><button type="button" class="btn btn-sm btn-icon btn-pure btn-outline delete-row-btn" data-toggle="tooltip" data-original-title="Delete"><i class="ti-close" aria-hidden="true"></i></button></td></tr>';
            
                //     //add it
                //     footable.appendRow(newRow);
                // });
            });       
        },
        addRow(doc,ln1,ln2,fn){
            length_rows = $("tbody tr").length + 1

            var addrow = $('#demo-foo-addrow2');
           
            //get the footable object
            var footable = addrow.data('footable');
                
            //build up the row we are wanting to add
            var newRow = '<tr><th><b>'+ length_rows +'</b></th><td>'+ doc +'</td><td>'+ ln1 + ' ' + ln2 + ' ' + fn +'</td><td> </td><td> </td><td class="text-center"> <button type="button" class="btn btn-warning btn-round btn-sm" data-toggle="modal" data-target="#ModalR" @click="Roles(item, key)"><i class="material-icons" style="font-size: 15px;">style</i><span style="position: relative;top: -2px;font-size: smaller;"> Roles</span></button><button class="btn btn-danger btn-round btn-sm btn-rc" @click="Pass(item, key)" style="width: 87px; max-height: 34px;"> <i class="material-icons">vpn_key</i> <div>Restablecer Contraseña</div> </button></td></tr>';
    
            //add it
            footable.appendRow(newRow);
        },
        listRole(id){
            const self = this
            axios.get('/security/users/roles/', { params: {person_id : id }})
            .then(function (response) {
                if (response.data.length > 0) {
                    self.roles = response.data
                }
            });
        },
        listUsers(){
            const self = this
            axios.get('/security/users/people/', {})
            .then(function (response) {
                if (response.data.length > 0) {
                    self.users = response.data
                    setTimeout(() => $('.show-tick').selectpicker('refresh'));
                }
                setTimeout(() =>{
                    $('table').trigger('footable_redraw');
                },120)
            });
        },
        selectaccess(detail,index,user){
            const self = this
            var csrfmiddlewaretoken = $("[name=csrfmiddlewaretoken]").val();
            const data = {
                uid       : user,
                accid    : detail.pk,
                very    : detail.fields.access,
                }
            axios({
                headers: {
                    'X-CSRFToken': csrfmiddlewaretoken,
                },
                method: 'POST',
                url: 'roles/',
                data: data
                }) .then(function (response) {
                    if(response.status=='200'){
                        if(detail.fields.access){
                            self.roles[index].fields.access = false
                            toastr.warning('¡Se quitó Acceso!', null, { "closeButton": false });
                            self.listUsers()
                        }
                        else{
                            self.roles[index].fields.access = true
                            toastr.success('¡Se agregó Acceso!', null, { "closeButton": false });
                            self.listUsers()
                        }
                    }
                })
        },

        Roles:function(item, index){
            this.formRole = {}
            this.listRole(item.pk)
            this.formRole.pk = item.pk;
            this.formRole = item;
            setTimeout(() => $('.show-tick').selectpicker('refresh'));
        },
        Pass:function(person, index){
            const self = this
            swal({
                title: "Desea restablecer la contraseña de " + person.fields.last_name0 + " " + person.fields.last_name1 + " " + person.fields.first_name,
                text: "La nueva contraseña será su documento de identidad",
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: "#DD6B55",
                confirmButtonText: "Si, Restablecer!",
                cancelButtonText: "No, Cancelar!",
                closeOnConfirm: false,
                closeOnCancel: false
            },
            function (isConfirm) {
                if (isConfirm) {
                    axios.get('/security/users/restpass/', { params: {person_id : person.pk }})
                    .then(function (response) {
                        swal({
                            title: "Realizado!",
                            text: "¡Se ha restablecido la contraseña a su documento de identidad!",
                            type: "success",
                            timer: 1200,
                            showConfirmButton: false
                        });
                        toastr.success('¡Se ha restablecido la contraseña a su documento de identidad!', null, { "closeButton": false });
                    }).catch(e => {
                        self.errors.push(e)
                    }) 
                }
                else{
                    swal({
                        title: "Cancelado!",
                        text: "No se restableció la contraseña",
                        type: "error",
                        timer: 1200,
                        showConfirmButton: false
                    });  
                }
            })
        },
        importLolcli(){
            const self = this;
            $(".page-loader-wrapper.import").css({"display": "block","background": "#acadce40"});
            axios.get('/security/users/importLolcli/', {})
            .then(function (response) {
                let people_lolcli = []
                if (response.data.length > 0) {
                    people_lolcli = response.data
                    people_lolcli.forEach(function (valor, indice, array) {
                        self.addRow(valor.fields.docid,valor.fields.last_name0,valor.fields.last_name1,valor.fields.first_name)
                    });
                    $(".page-loader-wrapper.import").css("display", "none");
                    $(".page-loader-wrapper.import").stop();
                    text_aviso = '¡Se han agregado '+ people_lolcli.length +' personas!'
                    toastr.success(text_aviso, null, { "closeButton": false });
                    self.createUser(people_lolcli);

                }else{
                    $(".page-loader-wrapper.import").css("display", "none");
                    toastr.warning('No existen registros nuevos para importar.', null, { "closeButton": false });
                }
            });
        },
        createUser(people){
            if (people.length > 0) {
                $(".createuser").css({"display": "block","background": "#acadce40"});
                setTimeout(function(){ 
                    people.forEach(function (valor, indice, array) {
                        axios.get('/security/users/importUsers/', {params: {person_id:valor.pk}})
                        .then(function (response) {
                            console.log('Usuario creado' + response.data)
                        })
                    });
                    let text_aviso = ''
                    if (people.length == 1) {
                        text_aviso = '¡Se ha creado '+ people.length +' usuario!'
                    }else{
                        text_aviso = '¡Se han creado '+ people.length +' usuarios!'
                    }
                     $(".createuser").css("display", "none");
                     toastr.success(text_aviso, null, { "closeButton": false });

                }, 2000);              
            }           
        },
        sendFormPerson(e){
            const self = this
            var csrfmiddlewaretoken = $("[name=csrfmiddlewaretoken]").val();
            var bodyFormData = new FormData(e.target);
            var document = $('#id_docid').val();
            var person_exist = false;
            self.users.forEach(function (valor, indice, array) {
                if(valor.fields.docid == document){
                    person_exist = true;
                }
            });
            if(person_exist){
                toastr.warning('¡Ya existe la persona!', null, { "closeButton": false });
            }else{
                axios({
                   headers: {'X-CSRFToken': csrfmiddlewaretoken },
                   method: 'POST',
                   url: '/security/users/people/',
                   data: bodyFormData,
                   }) .then(function (response) {
                       let people_lolcli = []
                       if (response.data.length > 0) {
                           people_lolcli = response.data
                           people_lolcli.forEach(function (valor, indice, array) {
                            //    self.addRow(valor.fields.docid,valor.fields.last_name0,valor.fields.last_name1,valor.fields.first_name)
                               self.users.push(valor)
                           });
                           toastr.success('¡Persona creada correctamente!', null, { "closeButton": false });
                           self.createUser(people_lolcli);
                           self.form = {}
                           $("#ModalPerson").modal('hide'); 
                       }
                   })
            }
        },
    },
})