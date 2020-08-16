unit Unit2;

interface

uses
  Classes, ComCtrls, IdBaseComponent, IdComponent, Dialogs,
  IdTCPConnection, IdTCPClient, IdHTTP, SysUtils, Windows, IdHeaderList, StrUtils;

type
  DLThread = class(TThread)
  private
    { Déclarations privées }
  protected
    procedure Execute; override;
  public
    http : TIdHTTP;
    terminated : boolean;
    item : TListItem;
    stream : TFileStream;
    link, filename, dest, tempdest : string;
    lastUpdate : cardinal;
  tempfile : string;
    count, countmax, speed, size : Int64;
    procedure IdHTTP1WorkBegin(ASender: TObject; AWorkMode: TWorkMode;
      AWorkCountMax: Int64);
    procedure IdHTTP1WorkEnd(ASender: TObject; AWorkMode: TWorkMode);
    procedure IdHTTP1Work(ASender: TObject; AWorkMode: TWorkMode;
  AWorkCount: Int64);
    procedure IdHTTP1HeadersAvailable(Sender: TObject;
  AHeaders: TIdHeaderList; var VContinue: Boolean);
    procedure Update;
    procedure UpdateSize;
    procedure delete;
  end;

implementation

uses Unit1;

procedure DLThread.delete;
begin
  terminated := true;
  http.OnHeadersAvailable := nil;
  http.OnWork := nil;
  http.OnWorkBegin := nil;
  http.OnWorkEnd := nil;
  http.Disconnect;
  stream.Free;
  SysUtils.DeleteFile(tempfile);
end;

procedure DLThread.IdHTTP1HeadersAvailable(Sender: TObject;
  AHeaders: TIdHeaderList; var VContinue: Boolean);
var content : string;
begin
  content := AHeaders.Values['Content-Disposition'];
  filename := Copy(content, pos('=', content)+2, length(content)-pos('=', content)-2);
  size := StrToInt64(AHeaders.Values['Content-Length']) div 1024 div 1024;
  Synchronize(UpdateSize);
end;

procedure DLThread.IdHTTP1WorkBegin(ASender: TObject; AWorkMode: TWorkMode;
  AWorkCountMax: Int64);
begin
  if AWorkMode = wmRead then //uniquement quand le composant recoit des données
  begin
  count := 0;
  countmax := AWorkCountMax;
  Synchronize(Update);
  end;
end;

procedure DLThread.IdHTTP1WorkEnd(ASender: TObject; AWorkMode: TWorkMode);
begin
  count := countmax + 1;
  Synchronize(Update);
end;

procedure DLThread.IdHTTP1Work(ASender: TObject; AWorkMode: TWorkMode;
  AWorkCount: Int64);
begin
  if AWorkMode = wmRead then
  begin
    if GetTickCount-lastUpdate > 1000 then
    begin
      speed := AWorkCount - count;
      count := AWorkCount;
      lastUpdate := GetTickCount;
      Synchronize(Update);
    end;
  end;
end;

procedure DLThread.Update;
begin
  if terminated then exit;
  
  if (count = 0) then
  begin
    Inc(Form1.currentDL);
    TItemData(item.Data).pb.Position := 0;
    item.SubItems[COL_STATE]:='En téléchargement';
    Form1.StatusBar1.SimpleText := 'Téléchargement en cours : ' + IntToStr(Form1.currentDL);
  end;
  if (count <= countmax) then
  begin
    item.SubItems[COL_SPEED] := IntToStr(speed div 1024) + ' Ko/s';
    try
      item.SubItems[COL_COMPLETED] := FormatFloat('0.##', 100*count/countmax) + '%';
      TItemData(item.Data).pb.Position := 100*count div countmax;
    except
      on e : Exception do item.SubItems[COL_COMPLETED] := '0 %';
    end;
  end
  else
  begin
    Dec(Form1.currentDL);
    Form1.StatusBar1.SimpleText := 'Téléchargement en cours : ' + IntToStr(Form1.currentDL);
    item.SubItems[COL_SPEED] := '';
    item.SubItems[COL_COMPLETED] := '';
    TItemData(item.Data).pb.Position := 100;
    item.SubItems[COL_STATE] := 'Terminé';
    Form1.checkShutdown;
  end;
end;

procedure DLThread.UpdateSize;
begin
  item.SubItems[COL_SIZE] := IntToStr(size) + ' Mo';
end;

procedure DLThread.Execute;
begin
  stream := nil;
  http := TIdHTTP.Create(item.ListView.Parent);
  with http do
  begin
    try
      tempfile := IncludeTrailingPathDelimiter(tempdest) + IntToStr(Random(MaxInt))+ IntToStr(Random(MaxInt));
      stream := TFileStream.Create(tempfile, fmCreate);

      OnHeadersAvailable := IdHTTP1HeadersAvailable;
      OnWork := IdHTTP1Work;
      OnWorkBegin := IdHTTP1WorkBegin;
      OnWorkEnd := IdHTTP1WorkEnd;
      terminated := false;
      Get(link, stream);
    finally
      stream.Free;
      Free;
    end;
  end;
  MoveFile(pchar(tempfile), pchar(IncludeTrailingPathDelimiter(dest) + filename));
end;

end.
