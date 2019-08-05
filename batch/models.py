from django.db import models
from django.contrib.auth.models import User
from .helpers import uploads_directory_path
from .validators import validate_file_extension



class Batch(models.Model):
    Batch_Id                                = models.AutoField(primary_key=True)
    Batch_Received_DateTime                 = models.DateTimeField(auto_now=True, null=True)
    Batch_Version                           = models.IntegerField(null=True)

    User_ID                                 = models.ForeignKey(User, on_delete=models.CASCADE)
    Project_Name                            = models.CharField(max_length=255, null=True)
    Project_Description                     = models.TextField(null=True)
    Project_IsPublic                        = models.BooleanField(default=False)
    Project_FileSourcePathName              = models.FileField(upload_to=uploads_directory_path,
                                                               validators=[validate_file_extension])

    AnalysisSource_ColumnsNameInput         = models.TextField(null=True)
    AnalysisSource_ColumnsNameOutput        = models.TextField(null=True)
    AnalysisSource_ColumnType               = models.TextField(null=True)
    AnalysisSource_CountLinesForTraining    = models.TextField(null=True)
    AnalysisSource_CountLinesForPrediction  = models.TextField(null=True)
    AnalysisSource_Errors                   = models.TextField(null=True)
    AnalysisSource_Warnings                 = models.TextField(null=True)

    ParameterCNN_Loss                       = models.TextField(null=True)
    ParameterCNN_Optimizer                  = models.TextField(null=True)
    ParameterCNN_Shape                      = models.TextField(null=True)

    Solving_DateTimeSending                 = models.DateTimeField(auto_now=True, null=True)
    Solving_CSVSolvedMergedFilePath         = models.CharField(max_length=255, null=True)
    Solving_DelayElapsed                    = models.IntegerField(null=True)
    Solving_Acuracy                         = models.BooleanField(default=False)
    Solving_TextError                       = models.TextField(null=True)
    Solving_TextWarning                     = models.TextField(null=True)
