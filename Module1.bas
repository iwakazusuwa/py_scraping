Attribute VB_Name = "Module1"
Sub 画像貼り付け()

    'セル幅、高さ
     With Columns("A")
          .Insert Shift:=xlToRight, copyorigin:=xlFormatFromLeftOrAbove
          .RowHeight = 83.25
     End With
     
     Columns.AutoFit
     
     Columns("A").ColumnWidth = 30
     
     
    'このファイルのPath
    Act_path = ActiveWorkbook.Path
    
    'このファイル名
    My_name = ActiveSheet.Name
    
    '順番に画像を張り付けながら、URLにリンクを張る
    t = 1
    Do Until Cells(t, 2) = Empty
       gazo = Act_path & "/" & Cells(t, 2) & "/" & Replace(Cells(t, 3), " ", "")
       Cells(t, 1).Select
       
        
       With Sheets(My_name).Pictures.Insert(gazo)
           .Top = Cells(t, 1).Top
           .Height = 80
           .Cut
      End With
      
      With Sheets(My_name)
            .Cells(t, 1).Select
            .Paste
      End With



    Set hyplink = ActiveSheet.Hyperlinks.Add(anchor:=Cells(t, 4), Address:=Cells(t, 4))
    t = t + 1
    
    Loop
    
   'A1セルにスクロール
    Application.Goto Reference:=Range("A1"), Scroll:=True
   '完成メッセージ
    MsgBox "完成"

End Sub

