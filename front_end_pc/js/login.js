/**
 * Created by python on 18-6-23.
 */
var vm = new Vue({
    el:'#app',
    data:{
        host,
        user_error:false,
        pwd_error:false,
        username:'',
        password:'',

        user_error_message:'用户名错误',
        pwd_error_message:'密码错误',
        remember:false
    },
    methods:{
         // 获取url路径参数
        get_query_string: function(name){
            var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
            var r = window.location.search.substr(1).match(reg);
            if (r != null) {
                return decodeURI(r[2]);
            }
            return null;
        },
        // 检查用户名是否为空
        check_username:function () {
            if(!this.username){
                this.user_error = true;
                this.user_error_message='用户名不能为空';
            }else{
                this.user_error = false;
            }
        },
        // 检查密码是否为空
        check_pwd:function () {
            if(!this.password){
                this.pwd_error = true;
                this.pwd_error_message='密码不能为空';
            }else{
                this.pwd_error = false;
            }
        },
        // 登陆
        on_submit:function () {
            // 不为空
            this.check_username();
            this.check_pwd();
            // 登陆请求
            if(this.user_error==false&&this.pwd_error==false){
                axios.post(this.host + '/authorizations/',
                    {username:this.username, password:this.password},
                    {responseType:'json'})
                    .then(response=>{
                        // 使用浏览器本地存储保存token
                        if (!this.remember){
                            localStorage.clear();
                            sessionStorage.username = response.data.username;
                            sessionStorage.user_id = response.data.id;
                            sessionStorage.token = response.data.token;
                        }
                        else{
                            sessionStorage.clear();
                            localStorage.username = response.data.username;
                            localStorage.user_id = response.data.id;
                            localStorage.token = response.data.token;
                        }

                        // 登陆成功，请求地址查询字符串中是否有next,有则跳转，无则去首页
                        var goto_url = this.get_query_string('next');
                        if (goto_url){
                            location.href = goto_url;
                        }else{
                            location.href = '/';
                        }
                    })
                    .catch(error=>{
                        this.pwd_error_message = '用户名或密码错误';
                        console.log(error.response.data)
                    })
            }
        },
        // QQ第三方登陆功能
        qq_login: function(){
            var state = this.get_query_string('next') || '/';
            axios.get(this.host + '/oauth/qq/authorization/?state=' + state, {
                    responseType: 'json'
                })
                .then(response => {
                    location.href = response.data.auth_url;
                })
                .catch(error => {
                    console.log(error.response.data);
                })
        }

    }
})