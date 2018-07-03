var vm = new Vue({
    el: '#app',
    data: {
        host: host,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        username: sessionStorage.username || localStorage.username,
        is_show_edit: false,
        provinces: [],
        cities: [],
        districts: [],
        addresses: [],
        limit: '',
        default_address_id: '',
        form_address: {
            receiver: '',
            province_id: '',
            city_id: '',
            district_id: '',
            place: '',
            mobile: '',
            tel: '',
            email: '',
        },
        error_receiver: false,
        error_place: false,
        error_mobile: false,
        error_email: false,
        editing_address_index: '', // 正在编辑的地址在addresses中的下标，''表示新增地址
        is_set_title: [],
        input_title: ''
    },
    // 渲染页面之前先请求所有的省份
    mounted: function () {
        axios.get(this.host + '/areas/', {
            responseType: 'json'
        })
            .then(response => {
                this.provinces = response.data;
            })
            .catch(error => {
                alert(error.response.data);
            });
        // 请求所有的地址信息
        this.get_addresses();
    },
    // 监听Vue中的属性，当属性值发生改变时，调用后面的匿名函数
    watch: {
        'form_address.province_id': function () {
            if (this.form_address.province_id) {
                axios.get(this.host + '/areas/' + this.form_address.province_id + '/', {
                    responseType: 'json'
                })
                    .then(response => {
                        this.cities = response.data.subs;
                    })
                    .catch(error => {
                        console.log(error.response.data);
                        this.cities = [];
                    });
            }
        },
        'form_address.city_id': function () {
            if (this.form_address.city_id) {
                axios.get(this.host + '/areas/' + this.form_address.city_id + '/', {
                    responseType: 'json'
                })
                    .then(response => {
                        this.districts = response.data.subs;
                    })
                    .catch(error => {
                        console.log(error.response.data);
                        this.districts = [];
                    });
            }
        },
    },
    methods: {
        // 退出
        logout: function () {
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },
        clear_all_errors: function () {
            this.error_receiver = false;
            this.error_mobile = false;
            this.error_place = false;
            this.error_email = false;
        },
        // 展示新增地址界面
        show_add: function () {
            this.clear_all_errors();
            this.editing_address_index = '';
            this.form_address.receiver = '';
            this.form_address.province_id = '';
            this.form_address.city_id = '';
            this.form_address.district_id = '';
            this.form_address.place = '';
            this.form_address.mobile = '';
            this.form_address.tel = '';
            this.form_address.email = '';
            this.is_show_edit = true;
        },
        // 展示编辑地址界面
        show_edit: function (index) {
            this.clear_all_errors();
            this.editing_address_index = index;
            // 只获取数据，防止修改form_address影响到addresses数据
            this.form_address = JSON.parse(JSON.stringify(this.addresses[index]));
            this.is_show_edit = true;
        },
        check_receiver: function () {
            if (!this.form_address.receiver) {
                this.error_receiver = true;
            } else {
                this.error_receiver = false;
            }
        },
        check_place: function () {
            if (!this.form_address.place) {
                this.error_place = true;
            } else {
                this.error_place = false;
            }
        },
        check_mobile: function () {
            var re = /^1[345789]\d{9}$/;
            if (re.test(this.form_address.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile = true;
            }
        },
        check_email: function () {
            if (this.form_address.email) {
                var re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;
                if (re.test(this.form_address.email)) {
                    this.error_email = false;
                } else {
                    this.error_email = true;
                }
            }
        },
        // 查询所有地址
        get_addresses: function () {
            axios.get(this.host + '/addresses/', {
                responseType: 'json',
                headers: {
                    'Authorization': 'JWT ' + this.token
                }
            })
                .then(response => {
                    this.addresses = response.data
                })
                .catch(error => {
                    this.addresses = error.response.data
                })
        },
        // 保存地址
        save_address: function () {
            this.check_receiver();
            this.check_place();
            this.check_mobile();
            this.check_email();
            var title = this.form_address.receiver + ' ' + this.form_address.place;
            this.form_address['title'] = title;
            if (this.error_mobile == false && this.error_place == false &&
                this.error_receiver == false && this.error_email == false) {
                if (this.editing_address_index !== '') {
                    axios.put(this.host + '/addresses/' + this.addresses[this.editing_address_index].id + '/', this.form_address,
                        {
                            responseType: 'json',
                            headers: {
                                'Authorization': 'JWT ' + this.token
                            }
                        })
                        .then(response => {
                            this.is_show_edit = false;
                            this.get_addresses();
                            alert('修改地址成功')
                        })
                        .catch(error => {
                            console.log(error.response.data)
                        })
                } else {
                    axios.post(this.host + '/addresses/',
                        this.form_address,
                        {
                            responseType: 'json',
                            headers: {
                                'Authorization': "JWT " + this.token
                            }
                        })
                        .then(response => {
                            this.is_show_edit = false;
                            this.get_addresses();
                            alert('新增地址成功')
                        })
                        .catch(error => {
                            alert(error.response)
                        })
                }

            }
        },
        // 删除地址 address_id通过url传递参数
        del_address: function (index) {
            axios.delete(this.host + '/addresses/' + this.addresses[index].id + '/', {
                responseType: 'json',
                headers: {
                    'Authorization': 'JWT ' + this.token
                }
            })
                .then(response => {
                    alert('删除地址成功');
                    // 删除地址成功后，将该地址从地址列表中删除
                    this.addresses.splice(index, 1);
                })
                .catch(error => {
                    alert(error.response.data)
                })
        },
        // 设置默认地址
        set_default: function (index) {
            //　put 请求的格式(url,data[,config]),即使没有数据要传递到后端，也必需用{}占位, 否则会将第二个参数作为请求参数
            axios.put(this.host + '/addresses/' + this.addresses[index].id + '/status/', {}, {
                responseType: 'json',
                headers: {
                    'Authorization': 'JWT ' + this.token
                }
            })
                .then(response => {
                    this.default_address_id = this.addresses[index].id;
                    alert('设置默认地址成功');
                })
                .catch(error => {
                    console.log(error.response.data);
                })

        },
        // 展示编辑标题
        show_edit_title: function (index) {
            this.input_title = this.addresses[index].title;
            for(var i=0; i<index; i++) {
                this.is_set_title.push(false);
            }
            this.is_set_title.push(true);
            // 也可以再次请求title信息
            // axios.get(this.host + '/addresses/' + this.addresses[index].id + '/show/',
            //     {
            //         responseType: 'json',
            //         headers: {
            //             'Authorization': 'JWT ' + this.token
            //         }
            //     })
            //     .then(response => {
            //         this.input_title = response.data.title
            //     })
            //     .catch(error => {
            //         console.log(error.response.data);
            //     })
        },
        // 保存地址标题
        save_title: function (index) {
            axios.put(this.host + '/addresses/' + this.addresses[index].id + '/edit/',
                {'title': this.input_title},
                {
                    responseType: 'json',
                    headers: {
                        'Authorization': 'JWT ' + this.token
                    }
                })
                .then(response=>{
                    this.addresses[index].title = response.data.title;
                    this.is_set_title=[];
                })
                .catch(error=>{
                    console.log(error.response.data);
                })
        },
        // 取消保存地址
        cancel_title: function (index) {
            this.is_set_title=[];
        }
    }
})