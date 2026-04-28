import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from script_editor.models import GlobalConfig

logger = logging.getLogger(__name__)


def send_task_notification(task_id, task_name, status, result_data=None, report_id=None):
    logger.info(f'Starting email notification for task {task_id}: {task_name}')
    try:
        config = GlobalConfig.get_config()

        logger.info(f'Email config: enable={config.email_enable}, host={config.email_smtp_host}, port={config.email_smtp_port}, user={config.email_username}, recipients={config.email_recipients}')

        if not config.email_enable:
            logger.info('Email notification disabled')
            return False

        if not all([config.email_smtp_host, config.email_username,
                   config.email_password, config.email_recipients]):
            logger.warning('Email configuration incomplete')
            return False

        recipients = [email.strip() for email in config.email_recipients.split(',') if email.strip()]

        if not recipients:
            logger.warning('No valid recipients')
            return False

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'[自动化测试] {task_name} - {"成功" if status == "completed" else "失败"}'
        msg['From'] = config.email_username
        msg['To'] = ', '.join(recipients)

        report_base_url = config.report_base_url.rstrip('/') if config.report_base_url else ''
        if report_id and report_base_url:
            # report_url = f"{report_base_url}/report/{report_id}?report={report_id}"
            report_url = f"{report_base_url}/?report={report_id}"
        elif report_base_url:
            # report_url = f"{report_base_url}/report/{task_id}?report={task_id}"
            report_url = f"{report_base_url}/?report={task_id}"
        else:
            # report_url = f"/report/{task_id}?report={task_id}"
            report_url = f"/?report={task_id}"

        is_multi_script = result_data and ('script_count' in result_data or 'script_results' in result_data)

        if is_multi_script:
            script_results = result_data.get('script_results', []) if result_data else []
            script_count = result_data.get('script_count', len(script_results)) if result_data else len(script_results)
            successful_scripts = result_data.get('successful_scripts', 0) if result_data else 0
            failed_scripts = result_data.get('failed_scripts', 0) if result_data else 0

            if not successful_scripts and not failed_scripts:
                for sr in script_results:
                    sr_status = sr.get('status', '')
                    if sr_status == 'completed':
                        successful_scripts += 1
                    elif sr_status == 'failed':
                        failed_scripts += 1

            task_status = status
            if task_status == 'completed':
                status_text = '成功'
                primary_color = '#10b981'
            else:
                if successful_scripts == 0:
                    status_text = '全部失败'
                    primary_color = '#ef4444'
                else:
                    status_text = '部分失败'
                    primary_color = '#f59e0b'

            total_duration = result_data.get('total_duration', 0) if result_data else 0
            pass_rate = result_data.get('pass_rate', 0) if result_data else 0
            if pass_rate is None:
                pass_rate = 0

            if total_duration is not None and total_duration > 0:
                if total_duration >= 60:
                    duration_str = f'{int(total_duration // 60)}分{total_duration % 60:.0f}秒'
                else:
                    duration_str = f'{total_duration:.2f}秒'
            else:
                duration_str = 'N/A'

            if pass_rate is not None:
                pass_rate_pct = f'{pass_rate:.1f}%'
            else:
                pass_rate_pct = 'N/A'

            passed_steps = successful_scripts
            failed_steps = failed_scripts
            total_steps = script_count

            stats_label = '脚本'

        else:
            step_results = result_data.get('step_results', []) if result_data else []
            pass_rate = result_data.get('pass_rate', 0) if result_data else 0
            total_steps = result_data.get('total_steps', len(step_results)) if result_data else len(step_results)
            passed_steps = result_data.get('passed_steps', 0) if result_data else 0
            failed_steps = result_data.get('failed_steps', 0) if result_data else 0
            skipped_steps = result_data.get('skipped_steps', 0) if result_data else 0
            total_duration = result_data.get('total_duration', 0) if result_data else 0

            is_success = status == 'completed'
            primary_color = '#10b981' if is_success else '#ef4444'
            status_text = '成功' if is_success else '失败'

            if total_duration and total_duration > 0:
                if total_duration >= 60:
                    duration_str = f'{int(total_duration // 60)}分{total_duration % 60:.0f}秒'
                else:
                    duration_str = f'{total_duration:.2f}秒'
            else:
                duration_str = 'N/A'

            if pass_rate is not None:
                pass_rate_pct = f'{pass_rate:.1f}%'
            else:
                pass_rate_pct = 'N/A'

            stats_label = '步骤'

        if is_multi_script:
            stats_cols = f'''
                            <tr>
                                <td align="center" style="padding: 8px;">
                                    <table role="presentation" cellpadding="0" cellspacing="0" style="text-align: center;">
                                        <tr>
                                            <td align="center" style="font-size: 28px; font-weight: 700; color: {primary_color}; line-height: 1;">{pass_rate_pct}</td>
                                        </tr>
                                        <tr>
                                            <td align="center" style="font-size: 12px; color: #6b7280; padding-top: 4px;">通过率</td>
                                        </tr>
                                    </table>
                                </td>
                                <td align="center" style="padding: 8px;">
                                    <table role="presentation" cellpadding="0" cellspacing="0" style="text-align: center;">
                                        <tr>
                                            <td align="center" style="font-size: 28px; font-weight: 700; color: #10b981; line-height: 1;">{passed_steps}</td>
                                        </tr>
                                        <tr>
                                            <td align="center" style="font-size: 12px; color: #6b7280; padding-top: 4px;">成功</td>
                                        </tr>
                                    </table>
                                </td>
                                <td align="center" style="padding: 8px;">
                                    <table role="presentation" cellpadding="0" cellspacing="0" style="text-align: center;">
                                        <tr>
                                            <td align="center" style="font-size: 28px; font-weight: 700; color: #ef4444; line-height: 1;">{failed_steps}</td>
                                        </tr>
                                        <tr>
                                            <td align="center" style="font-size: 12px; color: #6b7280; padding-top: 4px;">失败</td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td colspan="3" style="padding-top: 8px; font-size: 12px; color: #9ca3af; text-align: center;">总计 {total_steps} 个脚本</td>
                            </tr>'''
        else:
            stats_cols = f'''
                            <tr>
                                <td align="center" style="padding: 8px;">
                                    <table role="presentation" cellpadding="0" cellspacing="0" style="text-align: center;">
                                        <tr>
                                            <td align="center" style="font-size: 28px; font-weight: 700; color: {primary_color}; line-height: 1;">{pass_rate_pct}</td>
                                        </tr>
                                        <tr>
                                            <td align="center" style="font-size: 12px; color: #6b7280; padding-top: 4px;">通过率</td>
                                        </tr>
                                    </table>
                                </td>
                                <td align="center" style="padding: 8px;">
                                    <table role="presentation" cellpadding="0" cellspacing="0" style="text-align: center;">
                                        <tr>
                                            <td align="center" style="font-size: 28px; font-weight: 700; color: #10b981; line-height: 1;">{passed_steps}</td>
                                        </tr>
                                        <tr>
                                            <td align="center" style="font-size: 12px; color: #6b7280; padding-top: 4px;">通过</td>
                                        </tr>
                                    </table>
                                </td>
                                <td align="center" style="padding: 8px;">
                                    <table role="presentation" cellpadding="0" cellspacing="0" style="text-align: center;">
                                        <tr>
                                            <td align="center" style="font-size: 28px; font-weight: 700; color: #ef4444; line-height: 1;">{failed_steps}</td>
                                        </tr>
                                        <tr>
                                            <td align="center" style="font-size: 12px; color: #6b7280; padding-top: 4px;">失败</td>
                                        </tr>
                                    </table>
                                </td>
                                <td align="center" style="padding: 8px;">
                                    <table role="presentation" cellpadding="0" cellspacing="0" style="text-align: center;">
                                        <tr>
                                            <td align="center" style="font-size: 28px; font-weight: 700; color: #f59e0b; line-height: 1;">{skipped_steps}</td>
                                        </tr>
                                        <tr>
                                            <td align="center" style="font-size: 12px; color: #6b7280; padding-top: 4px;">跳过</td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td colspan="4" style="padding-top: 8px; font-size: 12px; color: #9ca3af; text-align: center;">总计 {total_steps} 个步骤</td>
                            </tr>'''

        html_content = f'''
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <title>自动化测试通知</title>
        </head>
        <body style="margin: 0; padding: 0; background-color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 24px 0;">
                <tr>
                    <td align="center" style="padding: 24px 16px;">
                        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width: 640px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);">
                            <tr>
                                <td style="background: linear-gradient(135deg, {primary_color} 0%, {primary_color}dd 100%); padding: 32px 24px; text-align: center;">
                                    <table role="presentation" width="64" height="64" cellpadding="0" cellspacing="0" style="margin: 0 auto 16px; background-color: rgba(255, 255, 255, 0.2); border-radius: 50%;">
                                        <tr>
                                            <td align="center" style="font-size: 32px; color: #ffffff;">{"&#10003;" if status_text in ['成功', '执行成功'] else "&#10007;"}</td>
                                        </tr>
                                    </table>
                                    <h1 style="margin: 0; font-size: 24px; font-weight: 700; color: #ffffff;">{status_text}</h1>
                                    <p style="margin: 8px 0 0; font-size: 14px; color: rgba(255, 255, 255, 0.9);">自动化测试任务执行通知</p>
                                </td>
                            </tr>

                            <tr>
                                <td style="padding: 24px 24px 16px;">
                                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color: #f9fafb; border-radius: 12px; border: 1px solid #e5e7eb;">
                                        <tr>
                                            <td style="padding: 16px;">
                                                <h2 style="margin: 0 0 12px; font-size: 16px; font-weight: 600; color: #111827;">任务摘要</h2>
                                                <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                                                    <tr>
                                                        <td style="padding: 6px 0; font-size: 14px; color: #6b7280; width: 80px;">任务名称</td>
                                                        <td style="padding: 6px 0; font-size: 14px; color: #111827; font-weight: 500;">{task_name}</td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 6px 0; font-size: 14px; color: #6b7280;">执行状态</td>
                                                        <td style="padding: 6px 0;">
                                                            <span style="display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; background-color: {primary_color}22; color: {primary_color};">{status_text}</span>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 6px 0; font-size: 14px; color: #6b7280;">执行时长</td>
                                                        <td style="padding: 6px 0; font-size: 14px; color: #111827;">{duration_str}</td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>

                            <tr>
                                <td style="padding: 0 24px 16px;">
                                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color: #f9fafb; border-radius: 12px; border: 1px solid #e5e7eb;">
                                        <tr>
                                            <td style="padding: 16px;">
                                                <h2 style="margin: 0 0 12px; font-size: 16px; font-weight: 600; color: #111827;">执行结果</h2>
                                                <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                                                    {stats_cols}
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>

                            <tr>
                                <td style="padding: 8px 24px 32px; text-align: center;">
                                    <table role="presentation" cellpadding="0" cellspacing="0" style="margin: 0 auto;">
                                        <tr>
                                            <td align="center" style="background-color: {primary_color}; border-radius: 10px;">
                                                <a href="{report_url}" target="_blank" style="display: inline-block; padding: 14px 32px; font-size: 15px; font-weight: 600; color: #ffffff; text-decoration: none;">查看完整报告 &rarr;</a>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>

                            <tr>
                                <td style="background-color: #f9fafb; padding: 16px 24px; text-align: center; border-top: 1px solid #e5e7eb;">
                                    <p style="margin: 0; font-size: 12px; color: #9ca3af;">此邮件由自动化测试系统自动发送，请勿回复。</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        '''

        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        logger.info(f'Sending email to {recipients} via {config.email_smtp_host}:{config.email_smtp_port}')

        if config.email_smtp_port == 465:
            with smtplib.SMTP_SSL(config.email_smtp_host, config.email_smtp_port) as server:
                server.login(config.email_username, config.email_password)
                server.sendmail(config.email_username, recipients, msg.as_string())
        else:
            with smtplib.SMTP(config.email_smtp_host, config.email_smtp_port) as server:
                server.starttls()
                server.login(config.email_username, config.email_password)
                server.sendmail(config.email_username, recipients, msg.as_string())

        logger.info(f'Email notification sent for task {task_id}')
        return True
    except Exception as e:
        logger.exception(f'Failed to send email for task {task_id}: {e}')
        return False
