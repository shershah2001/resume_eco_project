from django import forms
from account.models import MyUser,AddressModel,UserProfileModel


class user_register(forms.ModelForm):
    
    password=forms.CharField(max_length=100,widget=forms.PasswordInput(
        attrs={
            'class':'w-full border border-gray-400 rounded-lg px-4 py-2 text-black focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder':'please enter the password'
        }
    ))
    confirm_password=forms.CharField(max_length=100,widget=forms.PasswordInput(
        attrs={
            'class':'w-full border border-gray-400 rounded-lg px-4 py-2 text-black focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder':'please enter the password'
        }
    ))

    class Meta:
        model = MyUser
        fields=['username','email','first_name','last_name','password']
        widgets={
            'username':forms.TextInput(
                attrs={'class':'w-full border border-gray-400 rounded-lg px-4 py-2 text-black focus:outline-none focus:ring-2 focus:ring-blue-500','placeholder':'please enter the username'}
            ),
            'email':forms.EmailInput(
                attrs={
                    'class':'w-full border border-gray-400 rounded-lg px-4 py-2 text-black focus:outline-none focus:ring-2 focus:ring-blue-500',
                    'placeholder':'please enter an email'
                }
            ),
            'first_name':forms.TextInput(
                attrs={
                    'class':'w-full border border-gray-400 rounded-lg px-4 py-2 text-black focus:outline-none focus:ring-2 focus:ring-blue-500',
                    'placeholder':'please enter the first_name'
                }
            ),
            'last_name':forms.TextInput(
                attrs={
                    'class':'w-full border border-gray-400 rounded-lg px-4 py-2 text-black focus:outline-none focus:ring-2 focus:ring-blue-500',
                    'placeholder':'please enter the last_name'
                }
            )

        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if  password != confirm_password:
            raise forms.ValidationError("Password do not match.")
        return cleaned_data
    
    def save(self,commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if  commit:
            user.save()
        return user
        

    
class user_login(forms.Form):

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class':'w-full rounded-lg border border-gray-100 px-4 py-4 focus:outline-none focus:ring-2'
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class':'w-full rounded-lg border border-gray-100 px-4 py-4 focus:outline-none focus:ring-2'
            }
        )
    )
        


class address_form(forms.ModelForm):
    class Meta:
        model =  AddressModel
        fields =['name','mobile','pincode','locality','address','city','state','landmark','alternate_mobile','address_type']

        widgets={
            'name':forms.TextInput(
                attrs={
                    'class':'border p-3 rounded outline-none focus:border-blue-500'
                }
            ),
            'mobile':forms.TextInput(
                attrs={
                    'class':'border p-3 rounded outline-none focus:border-blue-500'
                }
            ),
            'pincode':forms.TextInput(
                attrs={
                    'class':'border p-3 rounded outline-none focus:border-blue-500'
                }
            ),
            'locality':forms.TextInput(
                attrs={
                    'class':"border p-3 rounded outline-none focus:border-blue-500"
                }
            ),
            'address':forms.Textarea(
                attrs={
                    'class':'border p-3 rounded outline-none focus:border-blue-500',
                    'rows':4
                }
            ),
            'city':forms.TextInput(
                attrs={
                    'class':'border p-3 rounded outline-none focus:border-blue-500'
                }
            ),
            'state':forms.Select(
                attrs={
                    'class':'border p-3 rounded outline-none focus:border-blue-500'
                }
            ),
            'landmark':forms.TextInput(
                attrs={
                    'class':'border p-3 rounded outline-none focus:border-blue-500'
                }
            ),
            'alternate_mobile':forms.TextInput(
                attrs={
                    'class':'border p-3 rounded outline-none focus:border-blue-500'
                }
            ),
            'address_type':forms.RadioSelect(
              attrs={
                  'class':'border border-gray-400'
              }
            )
        }
    

class UserProfileForm(forms.ModelForm):
    class Meta:
        model=UserProfileModel
        fields=['first_name','last_name','gender','email','mobile']