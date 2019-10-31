__author__ = 'zeewell'

from collections import namedtuple

ErrorInfo = namedtuple('ErrorInfo', 'id message')

version_too_low = ErrorInfo(-200, '你使用的天使挂号版本过低，需要更新到最新的天使挂号才能使用')

sys_server114_error = ErrorInfo(-100, '北京预约挂号平台系统出错，请稍候再试')
sys_params_error = ErrorInfo(-3, '请求参数错误')
sys_server_error = ErrorInfo(-2, '网络不稳定，请稍候再试')
sys_not_found = ErrorInfo(-1, '访问类型未知')


input_error = ErrorInfo(1, '输入错误')


user_not_exists = ErrorInfo(100, '用户不存在')
user_username_exists = ErrorInfo(101, '用户名已经存在')
user_email_exists = ErrorInfo(102, 'Email已经存在')
user_mobile_exists = ErrorInfo(103, '手机号已经存在')
user_invite_code_invalid = ErrorInfo(104, 'VIP激活码错误，或者已经被使用。请关注@天使健康助手')

user_id_number_exists = ErrorInfo(105, '证件号码已经存在')
user_authenticate_114server_error = ErrorInfo(106, '你的信息在北京预约挂号平台系统验证不成功，请确认你是否已经在该平台上注册，并检查你的证件号码、手机号、姓名是否正确')

user_password_error = ErrorInfo(110, '密码错误')
user_locked = ErrorInfo(111, '账号异常，无法登录。请联系客服解决。（可能的原因：已注销、黑名单、账号安全问题等）')
user_token_error = ErrorInfo(112, '登录已过期，请重新登录')

user_avatar_upload_failed = ErrorInfo(120, '用户头像保存失败')

user_points_not_enough = ErrorInfo(150, '你的积分不够，请先参加活动赚取积分。具体请参见使用帮助，或关注微博@天使健康助手')


appointments_not_exists = ErrorInfo(200, '号源不存在。')
appointments_out_service = ErrorInfo(201, '号源已停挂。')
appointments_empty = ErrorInfo(202, '当前号源已挂满，请尝试挂其他号源。或者可提交监控订单，一旦监控到有号，系统将会第一时间为你自动挂号')

order_not_exists = ErrorInfo(250, '订单不存在')
exists_conflict_order = ErrorInfo(251, '当前就诊人已经有一个同医院同科室相同日期的抢号订单，请等待该订单完成后再提交新订单')
order_canceled_failed_no_rights = ErrorInfo(252, '订单取消失败，你没有权限。')
order_canceled_failed_state_not_waiting = ErrorInfo(253, '订单取消失败，只能取消未开始的订单。如果是监控订单且正在监控中，请稍候再试，通常一分钟左右再重试取消即可。')
order_active_not_exists = ErrorInfo(254, '你当前没有运行中的挂号订单')
exists_running_monitor_order = ErrorInfo(255, '已经存在一个运行中的监控订单，在这个订单结束前，不能再提交新的监控订单。或者您可以取消当前正在运行的监控订单再重新提交。')


topic_board_locked = ErrorInfo(150, '圈子未激活')
topic_locked = ErrorInfo(151, '话题因被违反社区规定，被管理员关闭')


store_iap_receipt_invalid = ErrorInfo(20000, '票据非法')
store_iap_appstore_not_available = ErrorInfo(20001, 'App Store连接失败')
store_iap_sys_not_available = ErrorInfo(20002, '服务器当前不可用')
store_iap_verify_failed = ErrorInfo(20003, '票据验证失败')
store_iap_used_already = ErrorInfo(20004, '票据已使用')

# user_not_exist = ErrorInfo(1, u'')
# user_not_exist = ErrorInfo(1, u'')
# user_not_exist = ErrorInfo(1, u'')
# user_not_exist = ErrorInfo(1, u'')
# user_not_exist = ErrorInfo(1, u'')
# user_not_exist = ErrorInfo(1, u'')
# user_not_exist = ErrorInfo(1, u'')
# user_not_exist = ErrorInfo(1, u'')
# user_not_exist = ErrorInfo(1, u'')
# user_not_exist = ErrorInfo(1, u'')
