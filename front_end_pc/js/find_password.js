/**
 * Created by python on 18-6-24.
 */
var vm = new Vue({
    el:'#app',
    data:{
        host,
        user_error : false,
        image_code_error:false,

        username:'',
        image_code:'',
        image_code_id:'',
        image_code_url:'',
        user_error_message:'请填写账号名',
        image_code_error_message:'请填写验证码',
    },
    mounted:function () {
		this.generate_image_code();
    },
    methods:{
        generate_uuid: function(){
			var d = new Date().getTime();
			if(window.performance && typeof window.performance.now === "function"){
				d += performance.now(); //use high-precision timer if available
			}
			var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
				var r = (d + Math.random()*16)%16 | 0;
				d = Math.floor(d/16);
				return (c =='x' ? r : (r&0x3|0x8)).toString(16);
			});
			return uuid;
		},
		generate_image_code:function () {
				// 生成uuid
			this.image_code_id = this.generate_uuid();
			// 修改src属性值
			this.image_code_url = this.host + '/image_code/' + this.image_code_id + '/'
        },
        check_username:function () {
            if(!this.username){
                this.user_error = true;
                this.user_error_message='用户名不能为空';
            }else{
                this.user_error = false;
            }
        },
        check_image_code:function () {
            if(!this.image_code){
                this.image_code_error = true;
                this.image_code_error_message='验证码不能为空';
            }else{
                this.image_code_error = false;
            }
        },
        // form_1_on_submit:function () {
        //     this.check_username();
        //     this.check_image_code();
        //     if(this.user_error==false&&this.image_code_error==false){
        //         axios.get(this.host + '/accounts/' + this.username + '/')
        //     }
        // }
    }
})