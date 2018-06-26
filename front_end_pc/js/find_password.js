/**
 * Created by python on 18-6-24.
 */
var vm = new Vue({
    el: '#app',
    data: {
        host,
        // 图片id, url
        image_code_id: '',
        image_code_url: '',

        username: '',
        image_code: '',
        mobile: '',
        access_token: '',
        sms_code: '',
        user_id: '',
        password: '',
        password2: '',

        sending_flag: false,
        error_username: false,
        error_image_code: false,
        error_mobile: false,
        error_sms_code: false,
        error_password: false,
        error_check_password: false,

        error_username_message: '',
        error_image_code_message: '',
        sms_code_tip: '获取短信验证码',
        jump_time:'',
        error_mobile_message: '',
        error_sms_code_message: '',
        error_password_message: '',
        error_check_password_message: '',

        //	控制表单显示
        is_show_form_1: true,
        is_show_form_2: false,
        is_show_form_3: false,
        is_show_form_4: false,
        //	控制进度条显示
        step_class: {
            'step-1': true,
            'step-2': false,
            'step-3': false,
            'step-4': false
        },
    },
    mounted: function () {
        this.generate_image_code();
    },
    methods: {
        generate_uuid: function () {
            var d = new Date().getTime();
            if (window.performance && typeof window.performance.now === "function") {
                d += performance.now(); //use high-precision timer if available
            }
            var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
                var r = (d + Math.random() * 16) % 16 | 0;
                d = Math.floor(d / 16);
                return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
            });
            return uuid;
        },
        generate_image_code: function () {
            // 生成uuid
            this.image_code_id = this.generate_uuid();
            // 修改src属性值
            this.image_code_url = this.host + '/image_code/' + this.image_code_id + '/'
        },
        check_username: function () {
            if (!this.username) {
                this.error_username = true;
                this.error_username_message = '用户名不能为空';
            } else {
                this.user_error = false;
            }
        },
        check_image_code: function () {
            if (!this.image_code) {
                this.error_image_code = true;
                this.error_image_code_message = '验证码不能为空';
            } else {
                this.error_image_code = false;
            }
        },
        check_mobile: function () {
            if (!this.mobile) {
                this.error_mobile = true;
                this.error_mobile_message = '手机号不能为空';
            } else {
                this.error_mobile = false;
            }
        },
        check_sms_code: function () {
            if (!this.sms_code) {
                this.error_sms_code_message = '请填写短信验证码';
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },
        send_sms_code: function () {
            // 判断是否在60s内发送过短信
            if (this.sending_flag == true) {
                return;
            }
            this.sending_flag = true;
            this.check_mobile();
            if (this.error_mobile == false) {
                axios.get(this.host + '/sms_code/',
                    {
                        params: {
                            'access_token': this.access_token
                        },
                        responseType: 'json'
                    })
                    .then(response => {
                        var num = 60;
                        // 设置一个计时器
                        var t = setInterval(() => {
                            if (num == 1) {
                                // 如果计时器到最后, 清除计时器对象
                                clearInterval(t);
                                // 将点击获取验证码的按钮展示的文本回复成原始文本
                                this.sms_code_tip = '获取短信验证码';
                                // 将点击按钮的onclick事件函数恢复回去
                                this.sending_flag = false;
                            } else {
                                num -= 1;
                                // 展示倒计时信息
                                this.sms_code_tip = num + '秒';
                            }
                        }, 1000)
                    })
                    .catch(error => {
                        if (error.response.data.status == 400) {
                            this.error_mobile_message = error.response.data;
                            this.sending_flag = false;
                        }
                    })
            }
        },

        form_1_on_submit: function () {
            this.check_username();
            this.check_image_code();
            if (this.error_username == false && this.error_image_code == false) {
                axios.get(this.host + '/accounts/' + this.username + '/sms/token/',
                    {
                        params: {
                            'image_code': this.image_code,
                            'image_code_id': this.image_code_id
                        },
                        responseType: 'json'
                    })
                    .then(response => {
                        this.mobile = response.data.mobile,
                            this.access_token = response.data.access_token,

                            // 改变进度条样式
                            this.step_class['step-1'] = false;
                            this.step_class['step-2'] = true;

                            // 改变表单
                            this.is_show_form_1 = false;
                            this.is_show_form_2 = true;

                    })
                    .catch(error => {
                        if (error.response.status = 400) {
                            this.error_image_code_message = '图片验证码错误';
                            this.error_image_code = true;
                        } else if (error.response.status == 404) {
                            this.error_username_message = '用户名或手机号不不存在';
                            this.error_username = true;
                        } else {
                            console.log(error.response.data);
                        }
                    })

            }
        },
        form_2_on_submit: function () {
            this.check_mobile();
            this.check_sms_code();
            if (this.error_mobile == false && this.error_sms_code == false) {
                axios.get(this.host + '/accounts/' + this.username + '/password/token/',
                    {
                        params: {
                            'sms_code': this.sms_code
                        },
                        responseType: 'json'
                    })
                    .then(response => {
                        this.access_token = response.data.access_token;
                        this.user_id = response.data.user_id;
                        // 改变进度条样式
                        this.step_class['step-2'] = false;
                        this.step_class['step-3'] = true;

                        // 改变表单
                        this.is_show_form_2 = false;
                        this.is_show_form_3 = true;
                    })
                    .catch(error=>{
                        console.log(error.response.data)
                    })
            }
        },
        check_pwd: function (){
            var len = this.password.length;
            if(len<8||len>20) {
                this.error_password = true;
                this.error_password_message='密码格式错误'
            } else {
                this.error_password = false;
            }
        },
        check_cpwd: function (){
           if(this.password!=this.password2) {
                this.error_check_password = true;
                this.error_check_password_message = '两次密码不一致'
            } else {
                this.error_check_password = false;
            }
        },
        form_3_on_submit:function () {
            this.check_pwd();
            this.check_cpwd();
            if (this.error_password==false&&this.error_password_message==false){
                axios.post(this.host + '/users/' + this.user_id + '/password/',
                    {
                        'password':this.password,
                        'password2':this.password2,
                        'access_token':this.access_token
                    },
                    {responseType:'json'})
                    .then(response=>{
                        // 改变进度条样式
                        this.step_class['step-3'] = false;
                        this.step_class['step-4'] = true;

                        // 改变表单
                        this.is_show_form_3 = false;
                        this.is_show_form_4 = true;

                        _this = this
                        // 5秒后跳转
                        var num = 10;
                        // 设置一个计时器
                        var t = setInterval(() => {
                            if (num == 1) {
                                // 如果计时器到最后, 清除计时器对象
                                clearInterval(t);
                            } else {
                                num -= 1;
                                // 展示倒计时信息
                                _this.jump_time = num + '秒后自动跳转回首页';
                            }
                        }, 1000);
                        location.href = '/'
                    })
                    .catch(error=>{
                        console.log(error.response.data);
                    })

            }

        },
    }
})