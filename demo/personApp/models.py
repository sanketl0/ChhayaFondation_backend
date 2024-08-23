from django.db import models

# Create your models here.
class Personal_Details(models.Model):
    gender = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Transgender', 'Transgender')
    ]

    blood_group = [
        ('A-', 'A-'),
        ('A+', 'A+'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-')
    ]

    status = [
        ('Pending', 'Pending'),
        ('Ongoing', 'Ongoing'),
        ('Solved', 'Solved'),
        ('Closed', 'Closed'),
    ]

    levels = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low')
    ]

    maritalstatus = [
        ('Married', 'Married'),
        ('Single', 'Single'),
        ('Widowed', 'Widowed'),
        ('Separated', 'Separated'),
        ('Divorced', 'Divorced')
    ]

    # this user is like we can only see data of one signed user
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None)
    person_name = models.CharField(max_length=100, db_index=True)
    nick_name = models.CharField(max_length=50, db_index=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, db_index=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, db_index=True)
    address = models.TextField(db_index=True)
    pincode = models.CharField(max_length=10, db_index=True)

    village = models.CharField(max_length=100, db_index=True)
    city = models.CharField(max_length=100, db_index=True)
    taluka = models.CharField(max_length=100, db_index=True)
    district = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100, db_index=True)
    country =models.CharField(max_length=100, db_index=True)

    date_of_birth = models.DateField(db_index=True)
    age = models.IntegerField(db_index=True)
    adhar_number =models.CharField(max_length=12,db_index=True,null=True, blank=True)
    contact_number = models.CharField(max_length=15, db_index=True)
    place_of_birth = models.CharField(max_length=100, db_index=True)
    birth_time = models.TimeField(db_index=True)

    nationality = models.CharField(max_length=50, db_index=True)
    mother_tongue = models.CharField(max_length=50, db_index=True)
    other_language = models.CharField(max_length=50, db_index=True)


    cast = models.CharField(max_length=50, db_index=True)
    sub_cast = models.CharField(max_length=50, db_index=True)
    religion = models.CharField(max_length=50, db_index=True )

    marital_status = models.CharField(max_length=15, choices=maritalstatus, db_index=True)
    gender = models.CharField(max_length=20, choices=gender, db_index=True)
    blood_group = models.CharField(max_length=10, choices=blood_group, db_index=True)
    family_members = models.TextField(db_index=True)

    pan_card = models.CharField(max_length=20, db_index=True)
    driving_licence = models.CharField(max_length=20, db_index=True)
    passport_number = models.CharField(max_length=20, db_index=True)
    voting_id = models.CharField(max_length=20, db_index=True)

    educational_details = models.TextField(db_index=True)
    occupation = models.CharField(max_length=100, db_index=True)
    level = models.CharField(choices=levels,max_length=10, db_index=True, null=True, blank=True)
    main_photo = models.ImageField(upload_to='person_photos/')
    case_status = models.CharField(choices=status, max_length=10, db_index=True, blank=True, null=True,default='Pending')
    is_deleted = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['person_name', 'nick_name']),
            models.Index(fields=['latitude', 'longitude', 'address', 'pincode']),
            models.Index(fields=['village', 'city', 'taluka', 'district', 'state', 'country']),
            models.Index(fields=['date_of_birth', 'age','adhar_number']),
            models.Index(fields=['contact_number', 'place_of_birth', 'birth_time']),
            models.Index(fields=['nationality', 'mother_tongue', 'other_language']),
            models.Index(fields=['cast', 'sub_cast']),
            models.Index(fields=['marital_status', 'gender', 'blood_group', 'family_members']),
            models.Index(fields=['pan_card', 'driving_licence', 'passport_number', 'voting_id']),
            models.Index(fields=['educational_details', 'occupation','level']),
            models.Index(fields=['main_photo','case_status']),

        ]

    def __str__(self):
        return f'Personal details of {self.person_name}'

class Multiple_Photos(models.Model):
    person_name = models.ForeignKey(Personal_Details, on_delete=models.CASCADE, db_index=True)
    photos = models.ImageField(upload_to='person_photos/')

    class Meta:
        indexes = [
            models.Index(fields=['person_name']),
            models.Index(fields=['photos']),
        ]

    def __str__(self):
        return f'Photos of {self.person_name}'

class Police_Station_Location(models.Model):
    police_station_name = models.CharField(max_length=100, db_index=True)



    latitude = models.DecimalField(max_digits=9, decimal_places=6, db_index=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, db_index=True)

    address = models.TextField(db_index=True)
    pin_code = models.CharField(max_length=10, db_index=True)

    village = models.CharField(max_length=100, db_index=True)
    city = models.CharField(max_length=100, db_index=True)
    taluka = models.CharField(max_length=100, db_index=True)
    district = models.CharField(max_length=100, db_index=True)

    state = models.CharField(max_length=100, db_index=True)
    country = models.CharField(max_length=100, db_index=True)
    police_station_photo = models.ImageField(null=True, blank=True, upload_to='policeStations/')
    phone_number = models.CharField(max_length=15, db_index=True, null=True, blank=True)
    email = models.EmailField(max_length=254, db_index=True, null=True, blank=True)
    website = models.URLField(max_length=200, db_index=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['police_station_name','police_station_photo']),
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['address', 'pin_code']),
            models.Index(fields=['village', 'city', 'taluka', 'district']),
            models.Index(fields=['state', 'country']),
            models.Index(fields=['phone_number', 'email', 'website']),
        ]

    def __str__(self):
        return self.police_station_name

class Police_Complaint_Details(models.Model):
    person_name = models.ForeignKey(Personal_Details, on_delete=models.CASCADE, db_index=True)
    fir_number = models.CharField(max_length=50, db_index=True)
    is_deleted = models.BooleanField(default=False)
    police_station_name = models.ForeignKey(Police_Station_Location, on_delete=models.CASCADE, db_index=True)
    associate_police_officer_name = models.CharField(max_length=100, db_index=True)
    designation = models.CharField(max_length=50, db_index=True)
    fir_upload = models.FileField(upload_to='FIRs/', db_index=True, blank=True , null=True)

    class Meta:
        indexes = [
            models.Index(fields=['person_name', 'fir_number']),
            models.Index(fields=['police_station_name', 'associate_police_officer_name', 'designation']),
            models.Index(fields=['fir_upload']),
        ]

    def __str__(self):
        return f'Police complaint details of {self.person_name}'

class Missing_Event_Details(models.Model):
    person_name = models.ForeignKey(Personal_Details, on_delete=models.CASCADE, db_index=True)

    missing_date = models.DateField(db_index=True)
    missing_time = models.TimeField(db_index=True)

    location_of_missing = models.TextField(db_index=True)
    last_seen_location = models.TextField(db_index=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['person_name']),
            models.Index(fields=['missing_date', 'missing_time']),
            models.Index(fields=['location_of_missing', 'last_seen_location']),
        ]

    def __str__(self):
        return f'Missing details of {self.person_name}'