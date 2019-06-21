from django import forms
from btc.models import Btc


class AddBtcForm(forms.ModelForm):

    """
    Form for adding coins
    """
    class Meta:
        model = Btc
        fields = ['usd', 'gbp', 'buy_usd', 'sell_usd']