# get emails that match the query you specify
results = search_messages(service, "Python Code")
print(f"Found {len(results)} results.")
# for each email matched, read it (output plain/text to console & save HTML and attachments)
for msg in results[:10]:
    read_message(service, msg)

# test send email
send_message(service, "sudarshandudhe.masters@gmail.com", "This is a subject", 
            "This is the body of the email")

# mark_as_read(service, "Google")



# make unread emails from email@domain.com
# mark_as_unread(service, "from: email@domain.com")


# messages_to_delete
messages_to_delete = search_messages(service, "category:updates")
len(messages_to_delete)
list_delete= messages_to_delete[::-1]
len(list_delete)
website_set={}
website_list=[]
for message in list_delete[::5]:
    try:
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        # parts can be the message body, or attachments
        payload = msg['payload']
        headers = payload.get("headers")
        parts = payload.get("parts")
        folder_name = "email"
        has_subject = False
        if headers:
            # this section prints email basic info & creates a folder for the email
            for header in headers:
                name = header.get("name")
                value = header.get("value")
                if name.lower() == 'from':
                    # we print the From address
                    if '@' in value:
                        website_list.append(value.split("@")[1].replace('>',''))
                if name.lower() == "date":
                    pass

    except Exception as e:
#         print(str(e))
        pass

website_set = set(website_list)
website_set



# results=delete_messages(service,"doorDash")

messages_to_delete = search_messages(service, "brninfotech.org")
len(messages_to_delete)

start = 0
end=1000
for i in range(int(len(messages_to_delete)/1000)+1):
    messages_to_delete[start:end]   
    if end>len(messages_to_delete):
        end=len(messages_to_delete)
    print(start,end)
    batch_messages_to_delete = messages_to_delete[start:end]
#     print(len(batch_messages_to_delete))
    service.users().messages().batchDelete(
        userId='me',
        body={
            'ids': [ msg['id'] for msg in batch_messages_to_delete]
        }
    ).execute()
    start = end
    end +=1000
    