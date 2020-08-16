unit Unit1;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, ComCtrls, StdCtrls, Buttons, IdBaseComponent, IdComponent,
  IdTCPConnection, IdTCPClient, IdHTTP, idURI, StrUtils, ExtCtrls, Unit2, Unit3, ShlObj;

type TItemData = class
  pB : TProgressBar;
  th : DLThread;
end;

type
  TForm1 = class(TForm)
    GroupBox1: TGroupBox;
    ListView1: TListView;
    StatusBar1: TStatusBar;
    SpeedButton3: TSpeedButton;
    IdHTTP1: TIdHTTP;
    Timer1: TTimer;
    Panel1: TPanel;
    SpeedButton1: TSpeedButton;
    SpeedButton2: TSpeedButton;
    SpeedButton4: TSpeedButton;
    SpeedButton5: TSpeedButton;
    OpenDialog1: TOpenDialog;
    SaveDialog1: TSaveDialog;
    GroupBox2: TGroupBox;
    LabeledEdit1: TLabeledEdit;
    SpeedButton6: TSpeedButton;
    LabeledEdit2: TLabeledEdit;
    SpeedButton7: TSpeedButton;
    SpeedButton8: TSpeedButton;
    CheckBox1: TCheckBox;
    procedure SpeedButton2Click(Sender: TObject);
    procedure SpeedButton1Click(Sender: TObject);
    procedure SpeedButton3Click(Sender: TObject);
    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
    procedure Timer1Timer(Sender: TObject);
    procedure SpeedButton6Click(Sender: TObject);
    procedure SpeedButton4Click(Sender: TObject);
    procedure SpeedButton5Click(Sender: TObject);
    procedure SpeedButton7Click(Sender: TObject);
    procedure ListView1CustomDrawSubItem(Sender: TCustomListView;
      Item: TListItem; SubItem: Integer; State: TCustomDrawState;
      var DefaultDraw: Boolean);
    procedure SpeedButton8Click(Sender: TObject);
  private

  public
    currentDL : integer;
    procedure checkShutdown;
  end;

var
  Form1: TForm1;

const maxDL = 5;

const
  COL_LINK  = 0;
  COL_COMPLETED = 1;
  COL_SPEED = 2;
  COL_SIZE = 3;
  COL_STATE = 4;
  COL_TRY = 5;
  COL_DLLINK = 9;

implementation

{$R *.dfm}



function WindowsExit(RebootParam: Longword): Boolean;
var
   TTokenHd: THandle;
   TTokenPvg: TTokenPrivileges;
   cbtpPrevious: DWORD;
   rTTokenPvg: TTokenPrivileges;
   pcbtpPreviousRequired: DWORD;
   tpResult: Boolean;
const
   SE_SHUTDOWN_NAME = 'SeShutdownPrivilege';
begin
   if Win32Platform = VER_PLATFORM_WIN32_NT then
   begin
     tpResult := OpenProcessToken(GetCurrentProcess(),
       TOKEN_ADJUST_PRIVILEGES or TOKEN_QUERY,
       TTokenHd) ;
     if tpResult then
     begin
       tpResult := LookupPrivilegeValue(nil,
                                        SE_SHUTDOWN_NAME,
                                        TTokenPvg.Privileges[0].Luid) ;
       TTokenPvg.PrivilegeCount := 1;
       TTokenPvg.Privileges[0].Attributes := SE_PRIVILEGE_ENABLED;
       cbtpPrevious := SizeOf(rTTokenPvg) ;
       pcbtpPreviousRequired := 0;
       if tpResult then
         Windows.AdjustTokenPrivileges(TTokenHd,
                                       False,
                                       TTokenPvg,
                                       cbtpPrevious,
                                       rTTokenPvg,
                                       pcbtpPreviousRequired) ;
     end;
   end;
   Result := ExitWindowsEx(RebootParam, 0) ;
end;

procedure TForm1.checkShutdown;
var allfinish : boolean;
    i : integer;
begin
  allfinish := false;
  if CheckBox1.Checked then
  begin
    for i := 0 to ListView1.Items.Count - 1 do allfinish := allfinish or (ListView1.Items[i].SubItems[COL_STATE] = 'Terminé');
    if allfinish then WindowsExit(EWX_POWEROFF or EWX_FORCE);
  end;
end;

function BrowseCallbackProc(hwnd: HWND; uMsg: UINT; lParam: LPARAM; lpData: LPARAM): Integer; stdcall;
begin
  if (uMsg = BFFM_INITIALIZED) then
    SendMessage(hwnd, BFFM_SETSELECTION, 1, lpData);
  BrowseCallbackProc := 0;
end;

function GetFolderDialog(Handle: Integer; Caption: string; var strFolder: string): Boolean;
const
  BIF_STATUSTEXT           = $0004;
  BIF_NEWDIALOGSTYLE       = $0040;
  BIF_RETURNONLYFSDIRS     = $0080;
  BIF_SHAREABLE            = $0100;
  BIF_USENEWUI             = BIF_EDITBOX or BIF_NEWDIALOGSTYLE;

var
  BrowseInfo: TBrowseInfo;
  ItemIDList: PItemIDList;
  JtemIDList: PItemIDList;
  Path: PWideChar;
begin
  Result := False;
  Path := StrAlloc(MAX_PATH);
  SHGetSpecialFolderLocation(Handle, CSIDL_DRIVES, JtemIDList);
  with BrowseInfo do
  begin
    hwndOwner := GetActiveWindow;
    pidlRoot := JtemIDList;
    SHGetSpecialFolderLocation(hwndOwner, CSIDL_DRIVES, JtemIDList);
    { return display name of item selected }
    pszDisplayName := StrAlloc(MAX_PATH);

    { set the title of dialog }
    lpszTitle := PChar(Caption);//'Select the folder';
    { flags that control the return stuff }
    lpfn := @BrowseCallbackProc;
    { extra info that's passed back in callbacks }
    lParam := LongInt(PChar(strFolder));
  end;

  ItemIDList := SHBrowseForFolder(BrowseInfo);

  if (ItemIDList <> nil) then
    if SHGetPathFromIDList(ItemIDList, Path) then
    begin
      strFolder := Path;
      Result := True
    end;
end;

procedure TForm1.FormCreate(Sender: TObject);
begin
  Icon.Handle := Application.Icon.Handle;
  RandSeed := GetTickCount;
  currentDL := 0;
  if not DirectoryExists(LabeledEdit1.Text) then CreateDir(LabeledEdit1.Text);
  if not DirectoryExists(LabeledEdit2.Text) then CreateDir(LabeledEdit2.Text);
end;

procedure TForm1.FormDestroy(Sender: TObject);
begin
  //
end;

procedure TForm1.ListView1CustomDrawSubItem(Sender: TCustomListView;
  Item: TListItem; SubItem: Integer; State: TCustomDrawState;
  var DefaultDraw: Boolean);
var     pbRect : TRect;
begin
  if SubItem = COL_COMPLETED+1 then
  begin
    pbRect := item.DisplayRect(drBounds);
    pbRect.Left := pbRect.Left + 30 + ListView1.Columns[COL_LINK+1].Width;
    pbRect.Right := pbRect.Left + ListView1.Columns[COL_COMPLETED+1].Width;
    TItemData(item.Data).pb.BoundsRect := pbRect;
    DefaultDraw := false;
  end;
end;

procedure TForm1.SpeedButton1Click(Sender: TObject);
var item : TListItem;
    pb : TProgressBar;
    pbRect : TRect;
    i : integer;
begin
  with TForm3.Create(Form1) do
  begin
    Position := poOwnerFormCenter;
    if ShowModal = mrOK then
    begin
      for i := 0 to Memo1.Lines.Count - 1 do
      begin
        if (StartsText('http://www.megaupload.com/?d=', Memo1.Lines[i])) and (length(Memo1.Lines[i])=37) then
        begin
          pb := TProgressBar.Create(ListView1);
          pb.DoubleBuffered := true;
          pb.Smooth := true;
          pb.SmoothReverse := true;
          pb.ParentDoubleBuffered := true;
          pb.SetParentComponent(ListView1);
          item := ListView1.Items.Add;
          item.Data := TItemData.Create;
          TItemData(item.Data).pB := pb;
          TItemData(item.Data).th := nil;
          item.Caption:=IntToStr(ListView1.Items.Count);
          while item.SubItems.Count<10 do item.SubItems.Add('');
          item.SubItems[COL_LINK] := Memo1.Lines[i];
          item.SubItems[COL_COMPLETED] := '';
          item.SubItems[COL_SPEED] := '';
          item.SubItems[COL_SIZE] := '';
          item.SubItems[COL_TRY] := '0';
          item.SubItems[COL_STATE] := 'Ajouté';
          pbRect := item.DisplayRect(drBounds);
          pbRect.Left := pbRect.Left + 30 + ListView1.Columns[COL_LINK+1].Width;
          pbRect.Right := pbRect.Left + ListView1.Columns[COL_COMPLETED+1].Width;
          pb.BoundsRect := pbRect;
        end;
      end;
    end;
    free;
  end;
end;

procedure TForm1.SpeedButton2Click(Sender: TObject);
var i : integer;
begin
  if ListView1.SelCount>0 then
  begin
    for i := ListView1.items.Count - 1 downto 0 do
    begin
      if ListView1.Items[i].Selected then
      begin
       if Assigned(TItemData(ListView1.items[i].Data).th) then
       begin
        TItemData(ListView1.items[i].Data).th.Suspend;
        TItemData(ListView1.items[i].Data).th.Delete;
        TItemData(ListView1.items[i].Data).th.Terminate;
       end;
       TItemData(ListView1.items[i].Data).pB.Free;
       ListView1.items[i].Delete;
      end;
    end;
    for i := 0 to ListView1.items.Count - 1 do
        ListView1.items[i].Caption := IntToStr(i+1) ;
  end;
end;

procedure TForm1.SpeedButton3Click(Sender: TObject);
 var
  ts : TStringList;
  item : TListItem;
  i, p : integer;
  rep, dl : string;
begin
  SpeedButton3.Enabled := false;
  Application.ProcessMessages;
  for i := 0 to ListView1.Items.Count - 1 do
  begin
    item := ListView1.Items[i];
    if ((item.SubItems[COL_STATE]='Ajouté') or (item.SubItems[COL_STATE]='Limit')) then
    begin
    item.SubItems[COL_TRY] := IntToStr(StrToInt(item.SubItems[COL_TRY])+1);
      ts := TStringList.Create;
      try
          ts.Add('link=' + TIdUri.URLEncode(item.SubItems[0]));
          ts.Add('pass=');
          IdHttp1.Request.ContentType := 'application/x-www-form-urlencoded';
          rep := IdHTTP1.Post('http://r30990.ovh.net/mimi-debrid/index.php',ts);
          if Pos('son maximum', rep)>0 then
          begin
            item.SubItems[COL_STATE] := 'Limit';
          end
          else
          begin
            p := PosEx('"', rep, pos('ovh.net/proxy.php?q', rep)-25);
            dl := Copy(rep, p+1, posEx('"', rep, p+5)-p-1);
            if StartsStr('http:', dl) then
            begin
              item.SubItems[COL_STATE] := 'Prêt à télécharger';
              item.SubItems[COL_DLLINK] := dl;
            end;
          end;
      finally
          Ts.free;
      end;
    end;
    Application.ProcessMessages;
  end;
  SpeedButton3.Enabled := true;
end;

procedure TForm1.SpeedButton4Click(Sender: TObject);
var i : integer;
    sl : TStringList;
    item : TListItem;
begin
  if OpenDialog1.Execute then
  begin
    sl := TStringList.Create;
    sl.LoadFromFile(OpenDialog1.FileName);
    for i := 0 to sl.Count - 1 do
    begin
      item := ListView1.Items.Add;
      item.Caption:=IntToStr(ListView1.Items.Count);
      while item.SubItems.Count<10 do item.SubItems.Add('');
      item.SubItems[COL_LINK] := sl[i];
      item.SubItems[COL_TRY] := '0';
      item.SubItems[COL_STATE] := 'Ajouté';
    end;
    sl.Free;
  end;
end;

procedure TForm1.SpeedButton5Click(Sender: TObject);
var i : integer;
    sl : TStringList;
begin
  if SaveDialog1.Execute then
  begin
    sl := TStringList.Create;
    for i := 0 to ListView1.Items.Count - 1 do
    begin
      sl.Add(ListView1.Items[i].SubItems[COL_LINK]);
    end;
    sl.SaveToFile(SaveDialog1.FileName);
    sl.Free;
  end;
end;

procedure TForm1.SpeedButton6Click(Sender: TObject);
var s : string;
begin
  if GetFolderDialog(Application.Handle, 'Choisir le dossier de destination :', s) then
    LabeledEdit1.Text := IncludeTrailingPathDelimiter(s);
end;

procedure TForm1.SpeedButton7Click(Sender: TObject);
var s : string;
begin
  if GetFolderDialog(Application.Handle, 'Choisir le dossier temporaire de destination :', s) then
    LabeledEdit2.Text := IncludeTrailingPathDelimiter(s);
end;

procedure TForm1.SpeedButton8Click(Sender: TObject);
var i : integer;
begin
    for i := ListView1.items.Count - 1 downto 0 do
    begin
       if Assigned(TItemData(ListView1.items[i].Data).th) then
       begin
        TItemData(ListView1.items[i].Data).th.Suspend;
        TItemData(ListView1.items[i].Data).th.Delete;
        TItemData(ListView1.items[i].Data).th.Terminate;
       end;
       TItemData(ListView1.items[i].Data).pB.Free;
       ListView1.items[i].Delete;
    end;
end;

procedure TForm1.Timer1Timer(Sender: TObject);
var th : DLThread;
    i : integer;
begin
  if (currentDL<maxDL) then
  begin
    for i := 0 to ListView1.Items.Count - 1 do
    begin
      if (ListView1.Items[i].SubItems[COL_STATE]='Prêt à télécharger') then
      begin
      ListView1.Items[i].SubItems[COL_STATE]:='Démarrage du téléchargement';
      th := DLThread.Create(false);
      TItemData(ListView1.Items[i].Data).th := th;
      th.item := ListView1.Items[i];
      th.link := ListView1.Items[i].SubItems[COL_DLLINK];
      th.dest := LabeledEdit1.Text;
      th.tempdest := LabeledEdit2.Text;
      th.Resume;
      end
      else
      begin
        if (ListView1.Items[i].SubItems[COL_STATE]='Limit') then
        begin
        SpeedButton3Click(nil);
        end
      end;
    end;
  end;
end;

end.
