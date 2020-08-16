object Form3: TForm3
  Left = 0
  Top = 0
  BorderIcons = []
  BorderStyle = bsSingle
  Caption = 'Ajouter des liens '
  ClientHeight = 323
  ClientWidth = 437
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  PixelsPerInch = 96
  TextHeight = 13
  object GroupBox1: TGroupBox
    AlignWithMargins = True
    Left = 3
    Top = 3
    Width = 431
    Height = 282
    Align = alClient
    Caption = 'Liste de liens (un par ligne)'
    TabOrder = 0
    ExplicitLeft = 8
    ExplicitTop = 8
    ExplicitWidth = 377
    ExplicitHeight = 225
    object Memo1: TMemo
      AlignWithMargins = True
      Left = 5
      Top = 18
      Width = 421
      Height = 259
      Align = alClient
      TabOrder = 0
      ExplicitWidth = 372
      ExplicitHeight = 202
    end
  end
  object Panel1: TPanel
    Left = 0
    Top = 288
    Width = 437
    Height = 35
    Align = alBottom
    BevelOuter = bvNone
    TabOrder = 1
    ExplicitTop = 287
    ExplicitWidth = 435
    object Button1: TButton
      Left = 262
      Top = 4
      Width = 75
      Height = 25
      Caption = 'OK'
      TabOrder = 0
      OnClick = Button1Click
    end
    object Button2: TButton
      Left = 343
      Top = 4
      Width = 75
      Height = 25
      Caption = 'Annuler'
      TabOrder = 1
      OnClick = Button2Click
    end
  end
end
