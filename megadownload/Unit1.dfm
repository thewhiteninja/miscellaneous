object Form1: TForm1
  Left = 0
  Top = 0
  Caption = 'MegaUpload Downloader'
  ClientHeight = 577
  ClientWidth = 752
  Color = clBtnFace
  DoubleBuffered = True
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  Position = poScreenCenter
  OnCreate = FormCreate
  OnDestroy = FormDestroy
  DesignSize = (
    752
    577)
  PixelsPerInch = 96
  TextHeight = 13
  object SpeedButton3: TSpeedButton
    Left = 651
    Top = 8
    Width = 96
    Height = 75
    Anchors = [akTop, akRight]
    Caption = 'T'#233'l'#233'charger'
    OnClick = SpeedButton3Click
  end
  object GroupBox1: TGroupBox
    Left = 0
    Top = 88
    Width = 752
    Height = 470
    Align = alBottom
    Anchors = [akLeft, akTop, akRight, akBottom]
    Caption = 'Liste des liens'
    TabOrder = 0
    object ListView1: TListView
      AlignWithMargins = True
      Left = 5
      Top = 18
      Width = 742
      Height = 414
      Align = alClient
      Columns = <
        item
          Caption = 'N'#176
          MaxWidth = 30
          MinWidth = 30
          Width = 30
        end
        item
          Caption = 'Lien'
          Width = 260
        end
        item
          Caption = 'Compl'#233't'#233
          MinWidth = 60
          Width = 65
        end
        item
          Caption = 'Vitesse'
          MinWidth = 65
          Width = 65
        end
        item
          Caption = 'Taille'
          MinWidth = 65
          Width = 70
        end
        item
          Caption = 'Etat'
          Width = 195
        end
        item
          Caption = 'Essais'
          MinWidth = 40
        end>
      DoubleBuffered = True
      GridLines = True
      MultiSelect = True
      RowSelect = True
      ParentDoubleBuffered = False
      TabOrder = 0
      ViewStyle = vsReport
      OnCustomDrawSubItem = ListView1CustomDrawSubItem
    end
    object Panel1: TPanel
      Left = 2
      Top = 435
      Width = 748
      Height = 33
      Align = alBottom
      BevelOuter = bvNone
      TabOrder = 1
      DesignSize = (
        748
        33)
      object SpeedButton1: TSpeedButton
        Left = 3
        Top = 3
        Width = 134
        Height = 25
        Caption = 'Ajouter des liens ...'
        OnClick = SpeedButton1Click
      end
      object SpeedButton2: TSpeedButton
        Left = 143
        Top = 3
        Width = 90
        Height = 25
        Caption = 'Supprimer'
        OnClick = SpeedButton2Click
      end
      object SpeedButton4: TSpeedButton
        Left = 559
        Top = 3
        Width = 90
        Height = 25
        Anchors = [akTop, akRight]
        Caption = 'Charger ...'
        OnClick = SpeedButton4Click
        ExplicitLeft = 308
      end
      object SpeedButton5: TSpeedButton
        Left = 655
        Top = 3
        Width = 90
        Height = 25
        Anchors = [akTop, akRight]
        Caption = 'Enregister ...'
        OnClick = SpeedButton5Click
        ExplicitLeft = 404
      end
      object SpeedButton8: TSpeedButton
        Left = 239
        Top = 3
        Width = 90
        Height = 25
        Caption = 'Tout supprimer'
        OnClick = SpeedButton8Click
      end
    end
  end
  object StatusBar1: TStatusBar
    Left = 0
    Top = 558
    Width = 752
    Height = 19
    Panels = <>
    SimplePanel = True
    SimpleText = 'T'#233'l'#233'chargement en cours : 0'
  end
  object GroupBox2: TGroupBox
    Left = 0
    Top = 6
    Width = 645
    Height = 76
    Anchors = [akLeft, akTop, akRight]
    Caption = 'Options'
    TabOrder = 2
    DesignSize = (
      645
      76)
    object SpeedButton6: TSpeedButton
      Left = 367
      Top = 20
      Width = 30
      Height = 21
      Anchors = [akTop, akRight]
      Caption = '...'
      OnClick = SpeedButton6Click
    end
    object SpeedButton7: TSpeedButton
      Left = 367
      Top = 47
      Width = 30
      Height = 21
      Anchors = [akTop, akRight]
      Caption = '...'
      OnClick = SpeedButton7Click
    end
    object LabeledEdit1: TLabeledEdit
      Left = 76
      Top = 20
      Width = 285
      Height = 21
      Anchors = [akLeft, akTop, akRight]
      EditLabel.Width = 61
      EditLabel.Height = 13
      EditLabel.Caption = 'Destination :'
      LabelPosition = lpLeft
      TabOrder = 0
      Text = 'D:\'
    end
    object LabeledEdit2: TLabeledEdit
      Left = 76
      Top = 47
      Width = 285
      Height = 21
      EditLabel.Width = 33
      EditLabel.Height = 13
      EditLabel.Caption = 'Temp :'
      LabelPosition = lpLeft
      TabOrder = 1
      Text = 'D:\Temp'
    end
    object CheckBox1: TCheckBox
      Left = 425
      Top = 22
      Width = 209
      Height = 17
      Caption = 'Eteindre '#224' la fin des t'#233'l'#233'chargements'
      TabOrder = 2
    end
  end
  object IdHTTP1: TIdHTTP
    AllowCookies = True
    HandleRedirects = True
    RedirectMaximum = 10
    ProxyParams.BasicAuthentication = False
    ProxyParams.ProxyPort = 0
    Request.ContentLength = -1
    Request.ContentRangeEnd = -1
    Request.ContentRangeStart = -1
    Request.ContentRangeInstanceLength = -1
    Request.Accept = 'text/html, */*'
    Request.BasicAuthentication = False
    Request.UserAgent = 'Firefox/3.6'
    Request.Ranges.Units = 'bytes'
    Request.Ranges = <>
    HTTPOptions = [hoForceEncodeParams]
    Left = 360
    Top = 136
  end
  object Timer1: TTimer
    Interval = 2000
    OnTimer = Timer1Timer
    Left = 320
    Top = 136
  end
  object OpenDialog1: TOpenDialog
    Left = 280
    Top = 136
  end
  object SaveDialog1: TSaveDialog
    Left = 240
    Top = 136
  end
end
