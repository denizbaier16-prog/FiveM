RegisterCommand('exotest', function()
    local message = 'GitHub-SFTP-Deployment funktioniert!'
    print('[EXO RP] ' .. message)
    TriggerEvent('chat:addMessage', {
        color = { 50, 220, 120 },
        args = { 'EXO RP', message }
    })
end, false)
