Private Sub Application_ItemSend(ByVal Item As Object, Cancel As Boolean)
    Dim objRecip As Recipient
    Dim strMsg As String
    Dim res As Integer
    Dim strBcc As String
    On Error Resume Next

    strBcc = "user@domain.com"

    Set objRecip = Item.Recipients.Add(strBcc)
    objRecip.Type = olBCC
    If Not objRecip.Resolve Then
        strMsg = "Could not resolve the Bcc recipient. " & _
                 "Do you want still to send the message?"
        res = MsgBox(strMsg, vbYesNo + vbDefaultButton1, _
                "Could Not Resolve Bcc Recipient")
        If res = vbNo Then
            Cancel = True
        End If
    End If

    Set objRecip = Nothing
End Sub
