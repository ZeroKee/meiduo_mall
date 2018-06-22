var vm = new Vue({
	el: '#app',
	data: {
		error_name: false,
		error_password: false,
		error_check_password: false,
		error_phone: false,
		error_allow: false,
		error_image_code: false,
		error_sms_code: false,

		username: '',
		password: '',
		password2: '',
		mobile: '',
		image_code: '',
		sms_code: '',
		allow: false,
		image_code_id:'',
		image_code_url:'http:127.0.0.1:8000/image_code/70d92016-47d8-4634-8fb2-cb5391a6ff7d/',
		host:'http://127.0.0.1:8000',
		sending_flag:false,
		sms_code_tip:'获取短信验证码',
		error_image_code_message:'请填写图片验证码',
		error_name_message:'请输入5-20个字符的用户',
		error_mobile_message:'您输入的手机号格式不正确',
		error_sms_code_message:'请填写短信验证码'
	},
	mounted:function () {
		this.generate_image_code();
    },
	methods: {
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
		check_username: function (){
			var len = this.username.length;
			if(len<5||len>20) {
				this.error_name = true;
			} else {
				this.error_name = false;
			}
			// 用户名唯一认证
			if (this.error_name==false){
				axios.get(this.host + '/username/' + this.username + '/count/',
					{
						responseType:'json'
					})
					.then(response=>{
						if (response.data.count>0){
							this.error_name_message = '用户名已存在';
							this.error_name = true;
						}else{
							this.error_name = false;
						}
					})
					.catch(error=>{
						console.log(error.response.data);
					})
			}
		},
		check_pwd: function (){
			var len = this.password.length;
			if(len<8||len>20){
				this.error_password = true;
			} else {
				this.error_password = false;
			}
		},
		check_cpwd: function (){
			if(this.password!=this.password2) {
				this.error_check_password = true;
			} else {
				this.error_check_password = false;
			}
		},
		check_phone: function (){
			var re = /^1[3-9]\d{9}$/;
			if(re.test(this.mobile)) {
				this.error_phone = false;
			} else {
				this.error_phone = true;
			}
			// 手机号唯一认证
			if (this.error_phone==false){
				axios.get(this.host + '/mobile/' + this.mobile + '/count/',
					{
						responseType:'json'
					})
					.then(response=>{
						if (response.data.count>0){
							this.error_mobile_message='手机号已存在';
							this.error_phone= true;
						}else{
							this.error_phone=false;
						}
					})
					.catch(error=>{
						console.log(error.response.data);
					})
			}
		},
		check_image_code: function (){
			if(!this.image_code) {
				this.error_image_code = true;
			} else {
				this.error_image_code = false;
			}
		},
		check_sms_code: function(){
			if(!this.sms_code){
				this.error_sms_code = true;
			} else {
				this.error_sms_code = false;
			}
		},
		check_allow: function(){
			if(!this.allow) {
				this.error_allow = true;
			} else {
				this.error_allow = false;
			}
		},
		// 注册
		on_submit: function(){
			this.check_username();
			this.check_pwd();
			this.check_cpwd();
			this.check_phone();
			this.check_sms_code();
			this.check_allow();

			if (this.error_name==false,
				this.error_password==false,
				this.error_check_password==false,
				this.error_phone==false,
				this.error_image_code == false,
				this.error_sms_code == false,
				this.error_allow == false){
				axios.post(this.host + '/users/', {
					'username':this.username,
					'mobile':this.mobile,
					'password':this.password,
					'password2':this.password2,
					'sms_code':this.sms_code,
					'allow':this.allow.toString()
				})
					.then(response=>{
						// 登陆状态保持

						// 跳转到首页
						location.href='/'
					})
					.catch(error=>{
						if (error.response.status == 400){
							this.error_sms_code_message = '短信验证码错误';
							this.error_sms_code = true;
						}
						console.log(error.response.data)
					})
			}

		},
        send_sms_code: function () {
			// 判断是否在60s内发送过短信
			if (this.sending_flag==true){
				return;
			}
			sending_flag = true;
			// 校验验证码和手机号是否为空
			this.check_image_code();
			this.check_phone();

			if (this.error_phone==true||this.error_image_code==true||
				this.sending_flag==true){
				return;
			}
			// 发送请求
			axios.get(this.host + '/sms_code/'+ this.mobile + '/count/',
				{
					params:{  // 查询参数，也可以写在地址中
						image_code:this.image_code,
						image_code_id:this.image_code_id
					},
					responseType: 'json'
				})

				// 请求成功后倒计时
				.then(response => {
					// 表示后端发送短信成功
					// 倒计时60秒，60秒后允许用户再次点击发送短信验证码的按钮
					var num = 60;
					// 定义一个变量来保存this对象
					_this = this;
					// 设置一个计时器
					var t = setInterval(() => {
						if (num == 1) {
							// 如果计时器到最后, 清除计时器对象
							clearInterval(t);
							// 将点击获取验证码的按钮展示的文本回复成原始文本
							_this.sms_code_tip = '获取短信验证码';
							// 将点击按钮的onclick事件函数恢复回去
							_this.sending_flag = false;
						} else {
							num -= 1;
							// 展示倒计时信息
							_this.sms_code_tip = num + '秒';
						}
					}, 1000, 60)
				})
				.catch(error => {
					if (error.response.status == 400) {
						this.error_image_code_message = '图片验证码有误';
						this.error_image_code = true;
					} else {
						console.log(error.response.data);  // 发送失败，将错误信息抛到控制台
					}
					this.sending_flag = false;  // 维护发送状态
				})
        }

	}
});

