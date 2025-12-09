class ReportConfigException(Exception):
  @staticmethod
  def email_list_required():
    return ReportConfigException("A list of one or more email addresses is required for email report types.")
  

class ReportException(Exception):
  @staticmethod
  def error_on_create(msg : str):
    return ReportException(f"Error creating a report: {msg}")
  
  @staticmethod
  def report_gen_fail():
    return ReportException("Server has indicated report generation failed.")

  @staticmethod
  def report_download_fail(url : str):
    return ReportException(f"Failed to download report from: {url}")
