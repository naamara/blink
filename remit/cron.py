from django_cron import CronJobBase, Schedule
from remit.cronupdaterates import cron_update_rates


class UpdateRates(CronJobBase):
    RUN_EVERY_MINS = 1 # every 2 hours
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'remit_update_rates'    # a unique code

    def do(self):
    	cron_update_rates()