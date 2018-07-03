var vm = new Vue({
    el: '#app',
    data: {
        host,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        // 三个密码
        username: '',
        error_now_password: false,
        error_password: false,
        error_check_password: false,

        now_password: '',
        password: '',
        password2: '',

        error_password_msg:'',
        error_check_password_msg:'',



    },
    mounted: function () {
        // 判断用户的登录状态
        if (this.user_id && this.token) {
            axios.get(this.host + '/user/', {
                // 向后端传递JWT token的方法
                headers: {
                    'Authorization': 'JWT ' + this.token
                },
                responseType: 'json',
            })
                .then(response => {
                    // 加载用户数据
                    this.user_id = response.data.id;
                    this.username = response.data.username;
                    this.mobile = response.data.mobile;
                    this.email = response.data.email;
                    this.email_active = response.data.email_active;
                })
                .catch(error => {
                    if (error.response.status == 401 || error.response.status == 403) {
                        location.href = '/login.html?next=/user_center_info.html';
                    }
                });
        } else {
            location.href = '/login.html?next=/user_center_info.html';
        }
    },
    methods: {
        // 检查当前是否输入了密码
        check_now_pwd: function () {
            var length = this.now_password.length;
            if (length < 8 || length > 20) {
                this.error_now_password = true;
                this.error_password_msg = '当前密码输入错误';
            }
            else {
                this.error_now_password = false;
            }
        },
        check_pwd: function () {
            var length = this.password.length;
            if (length < 8 || length > 20) {
                this.error_password = true;
                this.error_password_msg = '请输入8-20长度的密码';
            }
            else {
                this.error_password = false;
            }
        },
        check_cpwd: function () {
            if (this.password2 != this.password) {
                this.error_check_password = true;
                this.error_check_password_msg = '两次输入的密码不一致'
            }
            else {
                this.error_check_password = false;
            }
        },
        on_submit: function () {
            this.check_now_pwd();
            this.check_pwd();
            this.check_cpwd();
            if (this.error_now_password == false || this.error_password == false || this.error_check_password == false) {
                // TODO 发送请求
                axios.put(this.host + '/users/password/', {
                    now_password: this.now_password,
                    password: this.password,
                    password2: this.password2,
                }, {
                    // 头部发送token，校验登录状态
                    headers: {
                        'Authorization': 'JWT ' + this.token
                    },
                    // 头信息里面的responseType
                    responseType: 'json'
                }).then(response => {
                    // TODO 发送成功提示
                    alert('修改密码成功');
                    this.now_password = '';
                    this.password = '';
                    this.password2 = '';
                }).catch(error => {
                    if (error.response.status == 400) {
                        this.error_password = true;
                        alert('修改密码失败')
                    }
                    else {
                        console.log(error.response.data)
                    }
                })
            }

        }
    },

});