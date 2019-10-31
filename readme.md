一点说明：
```yaml
app_key_secret:
  "ca6a9eb8-3254-47b9-a1fd-b1db41d99487": 1f3ddb0f-9427-483d-99f4-75b9d578e66f
  "dd910e60-74cd-44d5-8dd0-e292deb6c7f0": 87c2dc5d-57a3-4b1f-a5aa-939fcfb732c1
  "8311a7d0-3949-43be-ab90-81d4495a0c12": 5889b1d7-ab29-44fc-976d-98470ae65b68
```
其中
- ca6a9eb8-3254-47b9-a1fd-b1db41d99487  => iOS App id
- dd910e60-74cd-44d5-8dd0-e292deb6c7f0  => Android App id
- 8311a7d0-3949-43be-ab90-81d4495a0c12  => WxProgram App id



python3 -m grpc.tools.protoc -I microserver/proto/ --python_out=microserver/ --grpc_python_out=microserver/ microserver/proto/pbaccount.proto
python3 -m grpc.tools.protoc -I microserver/proto/ --python_out=microserver/ --grpc_python_out=microserver/ microserver/proto/pbsms.proto

