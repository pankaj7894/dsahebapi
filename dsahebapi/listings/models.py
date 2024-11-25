from django.db import models
from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from django.core.validators import MaxValueValidator, MinValueValidator
from config.models import CustomUser, State, City, Location, Services, Specialization, Degree, University, College, Memberships, Registration
CustomUser = get_user_model()


class Education(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='educations')
    degree = models.ForeignKey(Degree, on_delete=models.DO_NOTHING, related_name='educations', blank=True, null=True)
    college = models.ForeignKey(College, on_delete=models.DO_NOTHING, related_name='educations', blank=True, null=True)
    year = models.PositiveIntegerField()
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_educations', blank=True, null=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='updated_educations', blank=True, null=True)

    def __str__(self):
        return f'{self.degree} - {self.user.name}'

    def clean(self):
        if self.year < 1900 or self.year > timezone.now().year:
            raise ValidationError('Year must be valid and between 1900 and current year.')

    class Meta:
        ordering = ['degree']
        verbose_name = 'Education'

class Training(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='training')
    degree = models.ForeignKey(Degree, on_delete=models.DO_NOTHING, related_name='training', blank=True, null=True)
    college = models.ForeignKey(College, on_delete=models.DO_NOTHING, related_name='training', blank=True, null=True)
    year = models.PositiveIntegerField()
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_Training', blank=True, null=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='updated_Training', blank=True, null=True)

    def __str__(self):
        return f'{self.degree} - {self.user.name}'

    def clean(self):
        if self.year < 1900 or self.year > timezone.now().year:
            raise ValidationError('Year must be valid and between 1900 and current year.')

    class Meta:
        ordering = ['degree']

class RegistrationList(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='registrationlist')
    name = models.ForeignKey(Registration, on_delete=models.DO_NOTHING, related_name='registrationlist')
    year = models.PositiveIntegerField()
    status = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_registrationlist', blank=True, null=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='updated_registrationlist', blank=True, null=True)
    def __str__(self):
        return self.name    

    class Meta:
        ordering = ['name']

class Experience(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='experiences')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    ongoing = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_experiences', blank=True, null=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='updated_experiences', blank=True, null=True)

    def __str__(self):
        return f'{self.title} - {self.user.name}'

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError('Start date cannot be after end date.')

    class Meta:
        ordering = ['title']


class Listing(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=100)
    description = models.TextField()
    contact_number = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING, related_name='listings')
    state = models.ForeignKey(State, on_delete=models.DO_NOTHING, related_name='listings')
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING, related_name='listings')
    map_link = models.URLField(blank=True, null=True)
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    status = models.BooleanField(default=True)
    search_tags = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    online_verified = models.BooleanField(default=False)
    offline_verified = models.BooleanField(default=False)
    services = models.ManyToManyField(Services, related_name='listings')
    qna = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    experienceyear = models.PositiveIntegerField()
    fee = models.PositiveIntegerField()
    profile_image = models.ImageField(upload_to='listing/profile_images', blank=True, null=True)
    banner_image = models.ImageField(upload_to='listing/banner_images', blank=True, null=True)
    video_link = models.URLField(blank=True, null=True)
    claimed = models.BooleanField(default=False, verbose_name='Profile Claimed')
    specialization = models.ManyToManyField(Specialization, related_name='listings')
    education = models.ManyToManyField(Education, related_name='listings')
    memberships = models.ManyToManyField(Memberships, related_name='listings')
    experience = models.ManyToManyField(Experience, related_name='listings')
    registration = models.ManyToManyField(RegistrationList, related_name='listings')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_listings', blank=True, null=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='updated_listings', blank=True, null=True)

    def clean(self):
        if self.profile_image:
            if self.profile_image.size > 2 * 1024 * 1024:
                raise ValidationError('Profile image size must be less than 2MB.')
            if not self.profile_image.name.endswith(('jpg', 'jpeg', 'png')):
                raise ValidationError('Profile image must be in JPG, JPEG, or PNG format.')

        if self.banner_image:
            if self.banner_image.size > 2 * 1024 * 1024:
                raise ValidationError('Banner image size must be less than 2MB.')
            if not self.banner_image.name.endswith(('jpg', 'jpeg', 'png')):
                raise ValidationError('Banner image must be in JPG, JPEG, or PNG format.')

        search_terms = [
            self.title,
            " ".join([service.name for service in self.services.all()]),
            " ".join([spec.name for spec in self.specialization.all()]),
            str(self.state.name),
            str(self.city.name),
            str(self.location.name),
        ]
        self.search_tags = " ".join(search_terms).lower()  # Join all terms and convert to lowercase

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class Availability(models.Model):
    SLOT_TIME_CHOICES = [
        ('5', '5 minutes'),
        ('10', '10 minutes'),
        ('15', '15 minutes'),
        ('30', '30 minutes'),
        ('45', '45 minutes'),
        ('60', '60 minutes'),
    ]
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='availabilities')
    day = models.CharField(max_length=10, choices=[('MONDAY', 'Monday'), ('TUESDAY', 'Tuesday'), 
                                                   ('WEDNESDAY', 'Wednesday'), ('THURSDAY', 'Thursday'), 
                                                   ('FRIDAY', 'Friday'), ('SATURDAY', 'Saturday'), 
                                                   ('SUNDAY', 'Sunday')])
    start_time = models.TimeField()
    end_time = models.TimeField()
    start_time2 = models.TimeField(blank=True, null=True)
    end_time2 = models.TimeField(blank=True, null=True)
    start_time3 = models.TimeField(blank=True, null=True)
    end_time3 = models.TimeField(blank=True, null=True)
    slot_time = models.CharField(max_length=3, choices=SLOT_TIME_CHOICES, default='15')
    max_in_slot = models.IntegerField(default=10)
    max_in_day = models.IntegerField(default=50)
    status = models.BooleanField(default=True)

    def clean(self):
        # Check for overlapping time slots
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("Start time cannot be after or equal to the end time.")
        
        # Check for overlapping time slots in second and third slots
        if self.start_time2 and self.end_time2:
            if self.start_time2 >= self.end_time2:
                raise ValidationError("Second slot start time cannot be after or equal to the second slot end time.")
            if self.start_time2 < self.end_time and self.end_time2 > self.start_time:
                raise ValidationError("Second slot overlaps with the first slot.")

        if self.start_time3 and self.end_time3:
            if self.start_time3 >= self.end_time3:
                raise ValidationError("Third slot start time cannot be after or equal to the third slot end time.")
            if self.start_time3 < self.end_time2 and self.end_time3 > self.start_time2:
                raise ValidationError("Third slot overlaps with the second slot.")

    def __str__(self):
        return f'{self.listing.title} - {self.day}'

    class Meta:
        ordering = ['listing', 'day']

class Unavailability(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='unavailabilities')  # Changed related_name
    dateofunavailability = models.DateField()
    allday = models.BooleanField(default=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    status = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_unavailabilities', blank=True, null=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='updated_unavailabilities', blank=True, null=True)
    def clean(self):
        if not self.allday and (not self.start_time or not self.end_time):
            raise ValidationError('Start time and end time are required if not an all-day unavailability.')

    def __str__(self):
        return f'{self.listing.title} - {self.dateofunavailability}'
    
class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])
    comment = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if not self.user:
            raise ValidationError('User is required for submitting a review.')
        if not self.listing:
            raise ValidationError('Who are you reviewing? Please select.')
        if self.rating not in range(1, 6):
            raise ValidationError('Rating must be between 1 and 5.')

    def __str__(self):
        return f'Review for {self.listing.title} by {self.user.name}'

    class Meta:
        ordering = ['created_at']



