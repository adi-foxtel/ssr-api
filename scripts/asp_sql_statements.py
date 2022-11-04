#!/usr/bin/env python3


getSsrServiceDetailByTsId_sql_query = "SELECT total.source_chan_id,\n"+\
    "total.cnt as total,\n"+\
    "NVL(DEFAULTS.cnt, 0) as DEFAULTS,\n"+\
    "NVL(clear.cnt, 0) as clear,\n"+\
    "service_name.name from (\n"+\
    "    select source_chan_id, count(*) cnt\n"+\
    "    from ssr.out_stream_comp\n"+\
    "    where out_stream_id = ?\n"+\
    "    group by source_chan_id\n"+\
    ") total\n"+\
    "LEFT OUTER JOIN (\n"+\
    "    select source_chan_id, count(*) cnt\n"+\
    "    from ssr.out_stream_comp\n"+\
    "    where NVL(ecm_key_num,-1) = NVL(SUBSTR(notes,instr(notes,'(')+1, (instr(notes,')')-instr(notes,'(')-1)) ,-1)\n"+\
    "    and source_chan_id in (\n"+\
    "        select source_chan_id\n"+\
    "        from ssr.out_stream\n"+\
    "        where sig_id = 1\n"+\
    "        and out_stream_id = ?\n"+\
    "    )\n"+\
    "    group by source_chan_id\n"+\
    ") DEFAULTS ON DEFAULTS.source_chan_id = total.source_chan_id\n"+\
    "LEFT OUTER JOIN (\n"+\
    "    select out_stream_comp.source_chan_id,\n"+\
    "    name\n"+\
    "    from ssr.out_stream_comp, ssr.si_service_name\n"+\
    "    where out_stream_comp.source_chan_id = si_service_name.si_service_key\n"+\
    "    and si_service_name.lang = 'eng'\n"+\
    "    group by out_stream_comp.source_chan_id, name\n"+\
    ") SERVICE_NAME ON service_name.source_chan_id = total.source_chan_id\n"+\
    "LEFT OUTER JOIN (\n"+\
    "    select source_chan_id, count(*) cnt\n"+\
    "    from ssr.out_stream_comp\n"+\
    "    where ecm_stream_num = 0\n"+\
    "    and out_stream_id = ?\n"+\
    "    group by source_chan_id\n"+\
    ") clear ON clear.source_chan_id = total.source_chan_id\n"+\
    "ORDER BY source_chan_id ASC"



getSsrScrambledTransportStream_sql_query = "SELECT total.out_stream_id,\n" + \
    "total.cnt as total,\n" + \
    "NVL(DEFAULTS.cnt, 0) as DEFAULTS,\n" + \
    "NVL(altered.cnt, 0) as altered,\n" + \
    "NVL(clear.cnt, 0) as clear from (\n" + \
    "select out_stream_id, count(*) cnt\n" + \
    "    from ssr.out_stream_comp\n" + \
    "    group by out_stream_id\n" + \
    ") total LEFT OUTER JOIN (\n" + \
    "    select out_stream_id, count(*) cnt\n" + \
    "    from ssr.out_stream_comp " + \
    "    where NVL(ecm_key_num,-1) <> NVL(SUBSTR(notes,instr(notes,'(')+1, (instr(notes,')')-instr(notes,'(')-1)) ,-1)\n" + \
    "    and out_stream_id in (\n" + \
    "        select out_stream_id\n" + \
    "        from ssr.out_stream\n" + \
    "        where sig_id = 1\n" + \
    "    ) group by out_stream_id\n" + \
    ") altered ON altered.out_stream_id = total.out_stream_id\n" + \
    "LEFT OUTER JOIN (\n" + \
    "    select out_stream_id,\n" + \
    "    count(*) cnt\n" + \
    "    from ssr.out_stream_comp\n" + \
    "    where NVL(ecm_key_num,-1) = NVL(SUBSTR(notes,instr(notes,'(')+1, (instr(notes,')')-instr(notes,'(')-1)) ,-1)\n" + \
    "    and out_stream_id in (\n" + \
    "        select out_stream_id\n" + \
    "        from ssr.out_stream\n" + \
    "        where sig_id = 1\n" + \
    "    ) group by out_stream_id\n" + \
    ") DEFAULTS ON DEFAULTS.out_stream_id = total.out_stream_id\n" + \
    "LEFT OUTER JOIN (\n" + \
    "    select out_stream_id,\n" + \
    "    count(*) cnt\n" + \
    "    from ssr.out_stream_comp\n" + \
    "    where ecm_stream_num = 0\n" + \
    "    group by out_stream_id\n" + \
    ") clear ON clear.out_stream_id = total.out_stream_id\n" + \
    "ORDER BY OUT_STREAM_ID ASC"

getScrambledLocalObj_sql_query = "SELECT out_stream_id,\n" + \
    "si_service_id,\n" + \
    "name,\n" + \
    "source_chan_id,\n" + \
    "comp_num,\n" + \
    "comp_type,\n" + \
    "ecm_stream_num,\n" + \
    "ecm_key_num,\n" + \
    "notes\n" + \
    "FROM scrambled.state\n" + \
    "ORDER BY out_stream_id, si_service_id"

Defaultcommand1_sql_query = "update SSR.out_stream_comp set notes = 'Default ECM_KEY_NUM = ('|| ecm_key_num || ')' where source_chan_id = ?"
Defaultcommand2_sql_query = "update SSR.out_stream_comp set notes = 'Default CLEAR' where source_chan_id = ? and ecm_stream_num = 0"

CLRcommand_sql_query = "update SSR.out_stream_comp set ecm_stream_num = 0, ecm_key_num = null where source_chan_id = ?"
SCRcommand_sql_query = "update SSR.out_stream_comp set ecm_stream_num = 1, ecm_key_num = SUBSTR(notes,instr(notes,'(')+1,(instr(notes,')')-instr(notes,'(')-1)) where   SUBSTR(notes,instr(notes,'(')+1,(instr(notes,')')-instr(notes,'(')-1)) is not null and source_chan_id  = ?"

