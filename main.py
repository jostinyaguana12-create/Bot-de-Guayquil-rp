import discord
from discord.ext import commands
from discord import app_commands
import json, os, asyncio
from datetime import datetime
import pytz
from threading import Thread
from flask import Flask

# ---------------- CONFIG ----------------
TOKEN = os.getenv("DISCORD_TOKEN")
STAFF_ROLE_ID = 1421247889421893811
ROL1 = 1421247889086353479
CANAL_ANUNCIOS = 1421247894610116683

# ✅ Nuevos canales
CANAL_BIENVENIDA = 1421247893926449242   # Canal de bienvenida
CANAL_DESPEDIDA = 1421247893926449243    # Canal de despedida

META_VOTOS = 1
DATA_FILE = "datos.json"

ROLES_USUARIOS = [
    1421247889388343341, 1421247889291743304, 1421247889187012765,
    1421247889086353482, 1421247889023176771, 1421247889023176765,
    1421247888952131724, 1421247888952131723, 1421247888952131719,
    1421247888952131717, 1421247888847011922
]
ROLES_BOTS = [1421247889187012767, 1421247889187012766]

# ---------------- CONFIG TICKETS ----------------
TICKET_DATA_FILE = "tickets.json"

CANALES_PANEL = {
    "alianza": 1421247895579000964,
    "ck": 1421247896334110914,
    "apelacion_ck": 1421247896334110915,
    "reporte_jugador": 1421247895822274564,
    "reporte_staff": 1421247895822274563,
    "bug": 1421247895822274565,           # reemplaza con tu canal de panel bug
    "general": 1421247895822274566,       # reemplaza con tu canal de panel general
    "reclamar_robo": 1421247895822274567, # reemplaza con tu canal de panel reclamo IC
    "creador_contenido":1421247897847988365 # reemplaza con tu canal de panel creadores
}

CATEGORIAS_TICKETS = {
    "alianza": 1421247902247813138,
    "ck": 1423415426628718693,
    "apelacion_ck": 1423415426628718693,
    "reporte_jugador": 1423413799771181147,
    "reporte_staff": 1423413799771181147,
    "bug": 1423418696340209796,           # reemplaza con tu categoría bug
    "general": 1423411657098661929,       # reemplaza con tu categoría general
    "reclamar_robo": 1423413964708118689,# reemplaza con tu categoría reclamo IC
    "creador_contenido": 1423425541960237136 # reemplaza con tu categoría creadores
}

ROLES_PING = {
    "alianza": 1421247889388343345,
    "ck": 1423412006257426675,
    "apelacion_ck": 1423412006257426675,
    "reporte_jugador": 1421247889421893803,
    "reporte_staff": 1421247889421893803,
    "bug": 1423412836528427111,            # reemplaza con tu rol ping bug
    "general": 1421247889421893803,       # reemplaza con tu rol ping general
    "reclamar_robo": 1421247889421893806, # reemplaza con tu rol ping reclamo IC
    "creador_contenido": 1423413177722343454 # reemplaza con tu rol ping creadores
}

CANAL_LOGS = 1421247902432493780

# ---- Manejo de datos ----
def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"advertencias": {}, "sanciones": {}, "bans": {}}

def guardar_datos(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

data = cargar_datos()

# ---- Manejo de tickets ----
def cargar_tickets():
    if os.path.exists(TICKET_DATA_FILE):
        with open(TICKET_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"paneles": {}, "tickets_abiertos": {}}

def guardar_tickets(data):
    with open(TICKET_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

tickets_data = cargar_tickets()

# ---- Función hora Ecuador ----
def hora_ecuador():
    tz = pytz.timezone('America/Guayaquil')
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

# ---- Config Bot ----
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ---- Variables de votación ----
votos_usuarios = set()
mensaje_votacion = None
votacion_activa = False

# ---- Decorador STAFF ----
def staff_only():
    async def predicate(interaction: discord.Interaction):
        if any(r.id == STAFF_ROLE_ID for r in interaction.user.roles):
            return True
        await interaction.response.send_message("🚫 No tienes permiso para usar este comando.", ephemeral=True)
        return False
    return app_commands.check(predicate)

# -------------------- EVENTOS --------------------
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🌐 {len(synced)} comandos sincronizados.")
    except Exception as e:
        print(f"❌ Error al sincronizar comandos: {e}")

    # Cargar cogs correctamente
    await bot.add_cog(Moderacion(bot))
    await bot.add_cog(Tickets(bot))

@bot.event
async def on_member_join(member):
    canal = bot.get_channel(CANAL_BIENVENIDA)
    embed = discord.Embed(
        title="🎉 ¡Bienvenido/a a Guayaquil RP! 🎉",
        description=(
            f"{member.mention}\n🌆 La ciudad virtual más viva de Ecuador, donde cada historia tiene su lugar.\n"
            "Aquí experimentarás un **RolePlay serio, divertido y realista**, y tú serás el protagonista de tu propia aventura.\n\n"
            "📜 **Normas básicas:**\n"
            "* Respeta a todos los jugadores y al staff. 🤝\n"
            "* Mantén un roleo serio y coherente. 🎭\n"
            "* Prohibido el uso de cheats o ventajas injustas. 🚫\n"
            "* Cumple las leyes y reglas del servidor. ⚖️\n\n"
            "💡 **Recuerda:** Tu imaginación es el límite, pero el respeto es la clave.\n"
            "✨ **Consejo:** Pasa por los canales de reglas y guías para comenzar con buen pie.\n\n"
            "🚀 ¡Prepárate para crear tu historia y vivir grandes momentos en **Guayaquil RP**!"
        ),
        color=discord.Color.blurple()
    )
    try: embed.set_thumbnail(url=member.avatar.url)
    except: pass
    embed.set_footer(text=f"Guayaquil RP | ⏰ {hora_ecuador()} | © Derechos reservados de Guayaquil RP")
    if canal: await canal.send(embed=embed)
    try: await member.send(embed=embed)
    except: pass

    roles = ROLES_BOTS if member.bot else ROLES_USUARIOS
    for rol_id in roles:
        rol = member.guild.get_role(rol_id)
        if rol:
            await member.add_roles(rol)

@bot.event
async def on_member_remove(member):
    canal = bot.get_channel(CANAL_DESPEDIDA)
    embed = discord.Embed(
        title="💖 Gracias por ser parte de Guayaquil RP",
        description=(f"{member.mention}\nEsperamos que hayas disfrutado tu tiempo en este gran servidor.\n"
                     "Recuerda que siempre tendrás un lugar para regresar y seguir roleando con respeto y dedicación."),
        color=discord.Color.red()
    )
    try: embed.set_thumbnail(url=member.avatar.url)
    except: pass
    embed.set_footer(text=f"Guayaquil RP | ⏰ {hora_ecuador()} | © Derechos reservados de Guayaquil RP")
    if canal: await canal.send(embed=embed)
    try: await member.send(embed=embed)
    except: pass

# ---------------- COGS ----------------
class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ticket(self, ctx, *, motivo=None):
        if motivo is None:
            motivo = "No especificado"
        await ctx.send(f"Ticket creado: {motivo}")

# -------------------- COMANDO /votaciones --------------------
@bot.tree.command(name="votaciones", description="Abrir votaciones para el servidor")
async def votaciones(interaction: discord.Interaction):
    global mensaje_votacion, votacion_activa, votos_usuarios
    votos_usuarios = set()
    votacion_activa = True

    embed = discord.Embed(
        title="🗳️ VOTACIÓN – Guayaquil RP 🗳️",
        description=(
            "¡Bienvenido/a a la votación de nuestro servidor Guayaquil RP!\n\n"
            "Antes de emitir tu voto, te invitamos a leer cuidadosamente toda la información importante:\n\n"
            "📘 **Conceptos**\n"
            "Conceptos básicos y avanzados de RolePlay\n\n"
            "📜 **Normativas y Reglas Generales**\n"
            "Normas de comportamiento dentro del servidor\n"
            "Reglas de interacción y roleo\n"
            "Sanciones y procedimientos\n\n"
            "⏳ **Recuerda:** leer todo antes de votar garantiza una participación consciente y justa."
            f"\n\n➜ ✅ **Meta de apertura:** {META_VOTOS} votos"
            f"\n➜ ✅ **Cantidad de votos:** 0/{META_VOTOS}"
        ),
        color=discord.Color.blurple()
    )
    embed.set_footer(text=f"Guayaquil RP | ⏰ {hora_ecuador()} | © Derechos reservados de Guayaquil RP")

    content = f"<@&{ROL1}>"
    canal = interaction.guild.get_channel(CANAL_ANUNCIOS)
    mensaje_votacion = await canal.send(content=content, embed=embed)

    await mensaje_votacion.add_reaction("✅")
    await mensaje_votacion.add_reaction("⏳")
    await mensaje_votacion.add_reaction("❌")

    await interaction.response.send_message("🗳️ **Votación abierta**", ephemeral=True)

# -------------------- REACCIONES --------------------
@bot.event
async def on_raw_reaction_add(payload):
    global votos_usuarios
    if mensaje_votacion is None or not votacion_activa:
        return
    if str(payload.emoji) != "✅":
        return

    user = bot.get_user(payload.user_id)
    if user.bot:
        return

    votos_usuarios.add(user)

    canal = bot.get_channel(payload.channel_id)
    msg = await canal.fetch_message(payload.message_id)
    embed = msg.embeds[0]

    new_desc = embed.description.rsplit("\n", 1)[0]
    embed.description = f"{new_desc}\n➜ ✅ **Cantidad de votos:** {len(votos_usuarios)}/{META_VOTOS}"
    embed.set_footer(text=f"Guayaquil RP | ⏰ {hora_ecuador()} | © Derechos reservados de Guayaquil RP")
    await msg.edit(embed=embed)

    if len(votos_usuarios) >= META_VOTOS:
        await abrir_servidor_auto(payload.guild_id)

# -------------------- FUNCIONES SERVIDOR --------------------
async def abrir_servidor_auto(guild_id):
    global votacion_activa
    votacion_activa = False

    guild = bot.get_guild(guild_id)
    canal = guild.get_channel(CANAL_ANUNCIOS)
    content = f"<@&{ROL1}>"

    embed = discord.Embed(
        title="🟢 SERVIDOR ABIERTO – Guayaquil RP 🟢",
        description=(
            "¡La espera terminó! 🎉\n"
            "El servidor **Guayaquil RP** está oficialmente abierto y listo para el roleo.\n\n"
            "🌆 **Qué encontrarás al entrar:**\n"
            "Explora una ciudad viva y llena de posibilidades.\n"
            "Participa en eventos y actividades.\n"
            "Crea historias únicas con otros jugadores.\n"
            "Disfruta de vehículos, negocios y lugares emblemáticos.\n\n"
            "🔗 **Entra ahora al juego:**\n"
            "[Haz clic aquí para unirte al juego en Roblox](https://www.roblox.com/es/games/133543223221838/GUAYAQUIL-RP-3)\n\n"
            "💬 **Si necesitas ayuda:**\n"
            "Nuestro staff está disponible para responder tus dudas.\n"
            "Para reportes, presenta pruebas claras (capturas o grabaciones).\n\n"
            "⏱️ Los jugadores que votaron tienen **15 minutos** para entrar o serán sancionados."
        ),
        color=discord.Color.green()
    )
    lista_votantes = "\n".join([user.mention for user in votos_usuarios]) or "Nadie votó"
    embed.add_field(name="🖥️ Usuarios que votaron", value=lista_votantes, inline=False)
    embed.set_footer(text=f"Guayaquil RP | ⏰ {hora_ecuador()} | © Derechos reservados de Guayaquil RP")

    await canal.send(content=content, embed=embed)

# -------------------- COMANDOS SERVIDOR --------------------
@bot.tree.command(name="abrir_servidor", description="Abrir el servidor manualmente")
@staff_only()
async def abrir_servidor(interaction: discord.Interaction):
    await interaction.response.send_message("🟢 **Servidor abierto**", ephemeral=True)
    await abrir_servidor_auto(interaction.guild_id)

@bot.tree.command(name="cerrar_servidor", description="Cerrar el servidor")
@staff_only()
async def cerrar_servidor(interaction: discord.Interaction):
    guild = interaction.guild
    canal = guild.get_channel(CANAL_ANUNCIOS)
    content = f"<@&{ROL1}>"

    embed = discord.Embed(
        title="🔴 SERVIDOR CERRADO – Guayaquil RP 🔴",
        description=(
            "📢 ¡Atención, querida comunidad!\n"
            "El servidor **Guayaquil RP** se encuentra cerrado.\n\n"
            "🌆 **Agradecimiento:**\n"
            "Gracias a todos los que participaron y compartieron historias.\n\n"
            "💡 **Recuerda:**\n"
            "⚠️ Puedes apelar warns injustos con pruebas.\n"
            "📝 Reporta usuarios con evidencias claras.\n"
            "🚫 Evita unirte cuando esté cerrado.\n\n"
            "✨ Aunque el servidor esté cerrado, las historias y recuerdos creados permanecerán siempre."
        ),
        color=discord.Color.red()
    )
    embed.set_footer(text=f"Guayaquil RP | ⏰ {hora_ecuador()} | © Derechos reservados de Guayaquil RP")

    await interaction.response.send_message("✅ **Servidor cerrado**", ephemeral=True)
    await canal.send(content=content, embed=embed)

@bot.tree.command(name="cerrar_votaciones", description="Cerrar las votaciones sin abrir el servidor")
@staff_only()
async def cerrar_votaciones(interaction: discord.Interaction):
    global votacion_activa, votos_usuarios
    votacion_activa = False
    votos_usuarios = set()
    await interaction.response.send_message("❌ **Votaciones cerradas y reiniciadas**", ephemeral=True)

# ---------------- COGS ----------------
class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ⚠️ Advertir
    @app_commands.command(name="advertir", description="⚠️ Advertir a un usuario (máx. 3).")
    @staff_only()
    async def advertir(self, interaction: discord.Interaction, miembro: discord.Member, motivo: str):
        user_id = str(miembro.id)
        lista = data["advertencias"].setdefault(user_id, [])
        if len(lista) >= 3:
            return await interaction.response.send_message(f"⚠️ {miembro.mention} ya tiene 3 advertencias.", ephemeral=True)
        caso = len(lista)+1
        lista.append({"motivo": motivo, "resp": interaction.user.name, "caso": caso})
        guardar_datos(data)

        emb = discord.Embed(title="⚠️ Nueva Advertencia", color=discord.Color.yellow())
        emb.add_field(name="👤 Nombre", value=miembro.mention, inline=False)
        emb.add_field(name="📄 Motivo", value=motivo, inline=False)
        emb.add_field(name="🛡️ Responsable", value=interaction.user.mention, inline=False)
        emb.add_field(name="📌 Caso", value=str(caso), inline=False)
        emb.set_footer(text=f"⏰ {hora_ecuador()} | © Derechos reservados de Guayaquil RP")
        await interaction.response.send_message(embed=emb)

    # ⛔ Sancionar
    @app_commands.command(name="sancionar", description="⛔ Sancionar a un usuario (máx. 8).")
    @staff_only()
    async def sancionar(self, interaction: discord.Interaction, miembro: discord.Member, motivo: str):
        user_id = str(miembro.id)
        lista = data["sanciones"].setdefault(user_id, [])
        if len(lista) >= 8:
            return await interaction.response.send_message(f"⛔ {miembro.mention} ya tiene 8 sanciones.", ephemeral=True)
        caso = len(lista)+1
        lista.append({"motivo": motivo, "resp": interaction.user.name, "caso": caso})
        guardar_datos(data)

        emb = discord.Embed(title="⛔ Nueva Sanción", color=discord.Color.red())
        emb.add_field(name="👤 Nombre", value=miembro.mention, inline=False)
        emb.add_field(name="📄 Motivo", value=motivo, inline=False)
        emb.add_field(name="🛡️ Responsable", value=interaction.user.mention, inline=False)
        emb.add_field(name="📌 Caso", value=str(caso), inline=False)
        emb.set_footer(text=f"⏰ {hora_ecuador()} | © Derechos reservados de Guayaquil RP")
        await interaction.response.send_message(embed=emb)

    # 🔨 Banear
    @app_commands.command(name="ban", description="🔨 Banear a un usuario del servidor.")
    @staff_only()
    async def ban(self, interaction: discord.Interaction, usuario: discord.Member, motivo: str):
        try:
            # Hora de Ecuador
            hora = datetime.now(pytz.timezone("America/Guayaquil")).strftime("%d/%m/%Y %H:%M:%S")

            # Embed que llega al DM del usuario
            dm_embed = discord.Embed(
                title="🔨 Has sido baneado",
                color=discord.Color.red(),
                description=(
                    f"Has sido baneado del servidor por: **{motivo}**\n\n"
                    f"Si deseas apelar este baneo, contacta a: {interaction.user.mention}."
                )
            )
            dm_embed.set_footer(text=f"⏰ {hora} | © Derechos reservados de Guayaquil RP")

            # Intentar enviar DM al usuario
            try:
                await usuario.send(embed=dm_embed)
            except:
                # No se pudo enviar DM (bloqueado, DMs cerrados)
                pass

            # Banea al usuario en el servidor
            await usuario.ban(reason=motivo)

            # Guardar datos en JSON
            user_id = str(usuario.id)
            lista = data.setdefault("bans", {}).setdefault(user_id, [])
            caso = len(lista) + 1
            lista.append({"motivo": motivo, "resp": interaction.user.name, "caso": caso})
            data["bans"] = data.get("bans", {})
            guardar_datos(data)

            # Embed de confirmación en el servidor
            embed_confirm = discord.Embed(
                title="🔨 Usuario Baneado",
                color=discord.Color.red(),
                description=f"Usuario {usuario.mention} ha sido baneado por: {motivo}"
            )
            embed_confirm.set_footer(text=f"⏰ {hora} | © Derechos reservados de Guayaquil RP")
            await interaction.response.send_message(embed=embed_confirm)

        except Exception as e:
            await interaction.response.send_message(f"❌ No se pudo banear: {e}", ephemeral=True)

    # 📋 Ver sanciones
    @app_commands.command(name="ver_sancion", description="📋 Ver sanciones de un usuario.")
    @staff_only()
    async def ver_sancion(self, interaction: discord.Interaction, miembro: discord.Member):
        lista = data["sanciones"].get(str(miembro.id), [])
        if not lista:
            return await interaction.response.send_message(f"✅ {miembro.mention} no tiene sanciones.", ephemeral=True)
        emb = discord.Embed(title=f"📋 Sanciones de {miembro.display_name}", color=discord.Color.red())
        for s in lista:
            emb.add_field(name=f"📌 Caso {s['caso']}", value=f"📄 {s['motivo']} | 🛡️ {s['resp']}", inline=False)
        emb.set_footer(text=f"⏰ {hora_ecuador()} | © Derechos reservados de Guayaquil RP")
        await interaction.response.send_message(embed=emb)

    # 📋 Ver advertencias
    @app_commands.command(name="ver_advertencia", description="📋 Ver advertencias de un usuario.")
    @staff_only()
    async def ver_advertencia(self, interaction: discord.Interaction, miembro: discord.Member):
        lista = data["advertencias"].get(str(miembro.id), [])
        if not lista:
            return await interaction.response.send_message(f"✅ {miembro.mention} no tiene advertencias.", ephemeral=True)
        emb = discord.Embed(title=f"📋 Advertencias de {miembro.display_name}", color=discord.Color.yellow())
        for a in lista:
            emb.add_field(name=f"📌 Caso {a['caso']}", value=f"📄 {a['motivo']} | 🛡️ {a['resp']}", inline=False)
        emb.set_footer(text=f"⏰ {hora_ecuador()} | © Derechos reservados de Guayaquil RP")
        await interaction.response.send_message(embed=emb)

    # 🧹 Quitar sanción
    @app_commands.command(name="quitar_sancion", description="🧹 Quitar una sanción específica de un usuario por caso.")
    @staff_only()
    async def quitar_sancion(self, interaction: discord.Interaction, miembro: discord.Member, caso: int):
        user_id = str(miembro.id)
        lista = data["sanciones"].get(user_id, [])
        for s in lista:
            if s["caso"] == caso:
                lista.remove(s)
                guardar_datos(data)
                embed = discord.Embed(
                    title="🧹 Sanción eliminada",
                    description=f"Se eliminó la sanción del **caso {caso}** de {miembro.mention}.",
                    color=0x2ECC71,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Motivo", value=s["motivo"], inline=False)
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        embed_error = discord.Embed(
            title="❌ Sanción no encontrada",
            description=f"No se encontró la sanción del caso {caso} para {miembro.mention}.",
            color=0xE74C3C,
            timestamp=datetime.utcnow()
        )
        await interaction.response.send_message(embed=embed_error, ephemeral=True)

    # 🧹 Quitar advertencia
    @app_commands.command(name="quitar_advertencia", description="🧹 Quitar una advertencia específica de un usuario por caso.")
    @staff_only()
    async def quitar_advertencia(self, interaction: discord.Interaction, miembro: discord.Member, caso: int):
        user_id = str(miembro.id)
        lista = data["advertencias"].get(user_id, [])
        for a in lista:
            if a["caso"] == caso:
                lista.remove(a)
                guardar_datos(data)
                embed = discord.Embed(
                    title="🧹 Advertencia eliminada",
                    description=f"Se eliminó la advertencia del **caso {caso}** de {miembro.mention}.",
                    color=0xF1C40F,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Motivo", value=a["motivo"], inline=False)
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        embed_error = discord.Embed(
            title="❌ Advertencia no encontrada",
            description=f"No se encontró la advertencia del caso {caso} para {miembro.mention}.",
            color=0xE74C3C,
            timestamp=datetime.utcnow()
        )
        await interaction.response.send_message(embed=embed_error, ephemeral=True)
     
      
# ================== VIEW DENTRO DEL TICKET ==================
class TicketInsideView(discord.ui.View):
    def __init__(self, tipo: str, usuario: discord.User):
        super().__init__(timeout=None)
        self.tipo = tipo
        self.usuario = usuario

    @discord.ui.button(label="🛠️ Reclamar Ticket", style=discord.ButtonStyle.blurple)
    async def reclamar_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        canal = interaction.channel
        if "reclamado_por" in tickets_data["tickets_abiertos"].get(str(canal.id), {}):
            return await interaction.response.send_message("⚠️ Este ticket ya fue reclamado.", ephemeral=True)

        tickets_data["tickets_abiertos"][str(canal.id)]["reclamado_por"] = interaction.user.id
        guardar_tickets(tickets_data)

        await canal.send(f"✅ Ticket reclamado por {interaction.user.mention}")
        await interaction.response.send_message("Has reclamado este ticket.", ephemeral=True)

    @discord.ui.button(label="🔒 Cerrar Ticket", style=discord.ButtonStyle.red)
    async def cerrar_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        canal = interaction.channel
        data_ticket = tickets_data["tickets_abiertos"].pop(str(canal.id), None)
        guardar_tickets(tickets_data)

        if data_ticket:
            guild = interaction.guild
            log_channel = guild.get_channel(CANAL_LOGS)

            transcript_file = await transcripts.create_transcript(canal, filename=f"ticket-{canal.name}.html")

            embed = discord.Embed(
                title="📕 Ticket Cerrado",
                color=discord.Color.red()
            )
            embed.add_field(name="Tipo", value=data_ticket["tipo"], inline=False)
            embed.add_field(name="Usuario", value=f"<@{data_ticket['usuario']}>", inline=False)
            if "reclamado_por" in data_ticket:
                embed.add_field(name="Reclamado por", value=f"<@{data_ticket['reclamado_por']}>", inline=False)
            embed.add_field(name="Cerrado por", value=interaction.user.mention, inline=False)
            embed.add_field(name="Canal", value=canal.name, inline=False)
            embed.set_footer(text=f"Hora: {hora_ecuador()} | © Derechos Reservados – Guayaquil RP")

            await log_channel.send(embed=embed, file=transcript_file)

        await interaction.response.send_message("🔒 Ticket cerrado, este canal será eliminado en 5s.", ephemeral=True)
        await asyncio.sleep(5)
        await canal.delete()


# ================== VIEW BOTONES PANEL ==================
class TicketView(discord.ui.View):
    def __init__(self, tipo: str):
        super().__init__(timeout=None)
        self.tipo = tipo

    @discord.ui.button(label="Abrir Ticket", style=discord.ButtonStyle.green, emoji="📩")
    async def abrir_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        categoria = discord.utils.get(guild.categories, id=CATEGORIAS_TICKETS[self.tipo])
        rol_ping = guild.get_role(ROLES_PING[self.tipo])

        canal = await guild.create_text_channel(
            name=f"{self.tipo}-ticket-{interaction.user.name}",
            category=categoria,
            topic=f"Ticket de tipo {self.tipo} abierto por {interaction.user}"
        )
        await canal.set_permissions(interaction.user, view_channel=True, send_messages=True)

        tickets_data["tickets_abiertos"][str(canal.id)] = {
            "tipo": self.tipo,
            "usuario": interaction.user.id
        }
        guardar_tickets(tickets_data)

        embed_dentro = PLANTILLAS_DENTRO[self.tipo]

        await canal.send(
            content=f"{rol_ping.mention} 📢 Nuevo ticket de {interaction.user.mention}",
            embed=embed_dentro,
            view=TicketInsideView(self.tipo, interaction.user)
        )

        await interaction.response.send_message(f"✅ Ticket creado en {canal.mention}", ephemeral=True)


# ================== COG TICKETS ==================
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("🔧 Tickets cargados.")
        await self.crear_paneles_automaticos()

        for tipo, msg_id in tickets_data["paneles"].items():
            for guild in self.bot.guilds:
                canal = guild.get_channel(CANALES_PANEL.get(tipo))
                if not canal:
                    continue
                try:
                    msg = await canal.fetch_message(msg_id)
                    await msg.edit(view=TicketView(tipo))
                except:
                    pass

    async def crear_paneles_automaticos(self):
        for tipo, canal_id in CANALES_PANEL.items():
            for guild in self.bot.guilds:
                canal = guild.get_channel(canal_id)
                if not canal:
                    continue

                if tipo in tickets_data["paneles"]:
                    continue

                embed = PLANTILLAS_FUERA[tipo]
                msg = await canal.send(embed=embed, view=TicketView(tipo))

                tickets_data["paneles"][tipo] = msg.id
                guardar_tickets(tickets_data)
                print(f"✅ Panel de {tipo} creado automáticamente en {canal.name}")

# ================== PLANTILLAS DE TICKETS ==================

PLANTILLAS_FUERA = {
    "alianza": discord.Embed(
        title="🤝 ¡Solicita una Alianza con Guayaquil RP!",
        description=(
            "Hola 👋, si representas a otro servidor y deseas formar una alianza con Guayaquil RP, "
            "por favor sigue estos pasos:\n"
            "1️⃣ Haz clic en 'Abrir Ticket' para enviar tu solicitud.\n"
            "2️⃣ Completa la información que se te pedirá:\n"
            "• Nombre del servidor/organización\n"
            "• Discord o contacto principal\n"
            "• Breve descripción del servidor\n"
            "• Tipo de alianza (promoción mutua, eventos, colaboración, etc.)\n"
            "💡 Nota: Revisaremos cada solicitud cuidadosamente y nos pondremos en contacto contigo lo antes posible.\n"
            "¡Esperamos poder colaborar juntos y crecer como comunidad! 🌟"
        ),
        color=discord.Color.green()
    ),
    "ck": discord.Embed(
        title="⚔️ Solicitud de CK – Guayaquil RP",
        description=(
            "Si deseas realizar un CK (Character Kill) en Guayaquil RP, abre un ticket haciendo clic en 'Abrir Ticket'.\n"
            "Antes de abrirlo, ten en cuenta:\n"
            "• Solo se aceptan CKs de personajes activos.\n"
            "• Debes tener pruebas claras o motivos válidos.\n"
            "Nuestro equipo revisará cada solicitud cuidadosamente antes de aprobarla.\n"
            "📌 Haz clic en Abrir Ticket para enviar tu solicitud y sigue las instrucciones dentro."
        ),
        color=discord.Color.red()
    ),
    "apelacion_ck": discord.Embed(
        title="⚔️ Apelación de CK – Guayaquil RP",
        description=(
            "Si recibiste un CK y consideras que fue injusto o deseas apelar, abre un ticket haciendo clic en 'Abrir Ticket'.\n"
            "Antes de abrirlo, ten en cuenta:\n"
            "• Solo se aceptan apelaciones válidas y recientes.\n"
            "• Debes tener motivos claros o pruebas que respalden tu apelación.\n"
            "📌 Haz clic en Abrir Ticket y completa la información solicitada dentro."
        ),
        color=discord.Color.orange()
    ),
    "reporte_jugador": discord.Embed(
        title="⚠️ Reporte de Jugador – Guayaquil RP",
        description=(
            "Si deseas reportar a un jugador por infracciones o comportamiento inapropiado, abre un ticket haciendo clic en 'Abrir Ticket'.\n"
            "Antes de abrirlo, asegúrate de:\n"
            "• Tener pruebas claras del incidente (capturas, videos, enlaces, etc.)\n"
            "• No usar el ticket para disputas personales sin fundamento\n"
            "• Respetar las reglas del servidor\n"
            "📌 Haz clic en Abrir Ticket y sigue las instrucciones dentro."
        ),
        color=discord.Color.yellow()
    ),
    "reporte_staff": discord.Embed(
        title="⚠️ Reporte de Staff – Guayaquil RP",
        description=(
            "Si deseas reportar a un miembro del staff por incumplimiento de reglas, abuso de funciones o comportamiento inapropiado, abre un ticket haciendo clic en 'Abrir Ticket'.\n"
            "Antes de abrirlo, asegúrate de:\n"
            "• Tener pruebas claras del incidente (capturas, videos, enlaces, etc.)\n"
            "• No usar el ticket para conflictos personales\n"
            "• Respetar las normas del servidor\n"
            "📌 Haz clic en Abrir Ticket y completa la información solicitada dentro."
        ),
        color=discord.Color.dark_red()
    ),
    "bug": discord.Embed(
        title="🐞 Reporte de Bug – Guayaquil RP",
        description=(
            "Si encontraste un bug, error o fallo dentro del servidor, abre un ticket haciendo clic en 'Abrir Ticket'.\n"
            "Antes de abrirlo, asegúrate de:\n"
            "• Tener pruebas claras del error (capturas, videos, enlaces, etc.)\n"
            "• Explicar de forma clara qué ocurrió y cómo reproducirlo\n"
            "• No usar el ticket para disputas personales\n"
            "📌 Haz clic en Abrir Ticket y completa la información solicitada dentro."
        ),
        color=discord.Color.magenta()
    ),
    "general": discord.Embed(
        title="📝 Ticket General – Guayaquil RP",
        description=(
            "Si deseas realizar alguna acción (Reclamar rol, Crear banda, Crear empresa, Solicitar rol de tienda oficial), abre un ticket haciendo clic en 'Abrir Ticket'.\n"
            "Antes de abrirlo, asegúrate de:\n"
            "• Tener toda la información necesaria\n"
            "• Seguir las reglas del servidor\n"
            "• Completar todos los campos dentro del ticket\n"
            "📌 Haz clic en Abrir Ticket y sigue las instrucciones dentro."
        ),
        color=discord.Color.blue()
    ),
    "reclamar_robo": discord.Embed(
        title="💰 Reclamar Robo IC – Guayaquil RP",
        description=(
            "Si robaste a otro jugador dentro del servidor y deseas reclamar el dinero o los bienes obtenidos IC, abre un ticket haciendo clic en 'Abrir Ticket'.\n"
            "Antes de abrirlo, asegúrate de:\n"
            "• Solo usar este ticket para reclamar lo robado dentro del juego\n"
            "• Tener claro el monto o los bienes obtenidos\n"
            "• El personal revisará tu solicitud antes de otorgar la recompensa"
        ),
        color=discord.Color.dark_gold()
    ),
    "creador_contenido": discord.Embed(
        title="🎥 Solicitud de Creador de Contenido – Guayaquil RP",
        description=(
            "Si deseas convertirte en Creador de Contenido oficial, abre un ticket haciendo clic en 'Abrir Ticket'.\n"
            "Antes de abrirlo, ten en cuenta:\n"
            "• Debes producir contenido relacionado con el servidor\n"
            "• Mantener un comportamiento respetuoso y dentro de las reglas\n"
            "📌 Completa toda la información dentro del ticket para evaluación"
        ),
        color=discord.Color.dark_purple()
    )
}

PLANTILLAS_DENTRO = {
    "alianza": discord.Embed(
        title="🎫 Solicitud de Alianza – Guayaquil RP",
        description=(
            "¡Hola! 👋 Gracias por abrir este ticket para solicitar una alianza con Guayaquil RP.\n"
            "Completa la siguiente información:\n"
            "1️⃣ Nombre del servidor/organización\n"
            "2️⃣ Discord o contacto principal\n"
            "3️⃣ Breve descripción del servidor/proyecto\n"
            "4️⃣ Tipo de alianza (Promoción mutua, eventos conjuntos, intercambios, etc.)\n"
            "5️⃣ Tiempo estimado de la alianza\n"
            "6️⃣ Comentarios adicionales\n"
            "🔔 Nuestro equipo revisará tu solicitud y responderá aquí dentro del ticket."
        ),
        color=discord.Color.green()
    ),
    "ck": discord.Embed(
        title="🎫 Formulario de CK – Guayaquil RP",
        description=(
            "¡Hola! 👋 Gracias por abrir este ticket para solicitar un CK.\n"
            "Completa la siguiente información:\n"
            "1️⃣ Nombre del personaje que solicita el CK\n"
            "2️⃣ Nombre del personaje que será eliminado\n"
            "3️⃣ Motivo del CK\n"
            "4️⃣ Evidencias (si aplica)\n"
            "5️⃣ ¿El CK es consensuado o por regla?\n"
            "6️⃣ Comentarios adicionales\n"
            "🔔 El equipo de administración revisará tu solicitud y responderá dentro del ticket."
        ),
        color=discord.Color.red()
    ),
    "apelacion_ck": discord.Embed(
        title="🎫 Formulario de Apelación de CK – Guayaquil RP",
        description=(
            "¡Hola! 👋 Gracias por abrir este ticket para apelar un CK.\n"
            "Completa la siguiente información:\n"
            "1️⃣ Nombre del personaje que recibió el CK\n"
            "2️⃣ Nombre del personaje que aplicó el CK\n"
            "3️⃣ Motivo de la apelación\n"
            "4️⃣ Evidencias o pruebas\n"
            "5️⃣ Fecha y hora del CK\n"
            "6️⃣ Comentarios adicionales\n"
            "🔔 Nuestro equipo revisará tu apelación y responderá dentro del ticket."
        ),
        color=discord.Color.orange()
    ),
    "reporte_jugador": discord.Embed(
        title="🎫 Formulario de Reporte – Guayaquil RP",
        description=(
            "¡Hola! 👋 Gracias por abrir este ticket para reportar a un jugador.\n"
            "Completa la siguiente información:\n"
            "1️⃣ Nombre del jugador reportado\n"
            "2️⃣ Nombre de tu personaje/usuario\n"
            "3️⃣ Motivo del reporte\n"
            "4️⃣ Evidencias\n"
            "5️⃣ Fecha y hora aproximada del incidente\n"
            "6️⃣ Comentarios adicionales\n"
            "🔔 El equipo de administración revisará tu reporte y responderá dentro del ticket."
        ),
        color=discord.Color.yellow()
    ),
    "reporte_staff": discord.Embed(
        title="🎫 Formulario de Reporte de Staff – Guayaquil RP",
        description=(
            "¡Hola! 👋 Gracias por abrir este ticket para reportar a un miembro del staff.\n"
            "Completa la siguiente información:\n"
            "1️⃣ Nombre del staff reportado\n"
            "2️⃣ Nombre de tu personaje/usuario\n"
            "3️⃣ Motivo del reporte\n"
            "4️⃣ Evidencias\n"
            "5️⃣ Fecha y hora aproximada del incidente\n"
            "6️⃣ Comentarios adicionales\n"
            "🔔 Nuestro equipo revisará tu reporte y responderá dentro del ticket."
        ),
        color=discord.Color.dark_red()
    ),
    "bug": discord.Embed(
        title="🎫 Formulario de Reporte de Bug – Guayaquil RP",
        description=(
            "¡Hola! 👋 Gracias por abrir este ticket para reportar un error.\n"
            "Completa la siguiente información:\n"
            "1️⃣ Descripción del error\n"
            "2️⃣ Pasos para reproducirlo\n"
            "3️⃣ Evidencias\n"
            "4️⃣ Fecha y hora aproximada\n"
            "5️⃣ Impacto del error (roleo, economía, misiones, interacción, etc.)\n"
            "6️⃣ Comentarios adicionales\n"
            "🔔 Nuestro equipo revisará tu reporte y responderá dentro del ticket."
        ),
        color=discord.Color.magenta()
    ),
    "general": discord.Embed(
        title="🎫 Formulario General – Guayaquil RP",
        description=(
            "¡Hola! 👋 Gracias por abrir este ticket.\n"
            "Completa la información según tu caso:\n"
            "1️⃣ Tipo de solicitud (Reclamar rol / Crear banda / Crear empresa / Solicitar rol de tienda oficial)\n"
            "2️⃣ Nombre del personaje/usuario\n"
            "3️⃣ Nombre de la banda, empresa o tienda (si aplica)\n"
            "4️⃣ Descripción o detalles de tu solicitud\n"
            "5️⃣ Evidencias o información adicional\n"
            "6️⃣ Comentarios adicionales\n"
            "🔔 Nuestro equipo revisará tu solicitud y responderá dentro del ticket."
        ),
        color=discord.Color.blue()
    ),
    "reclamar_robo": discord.Embed(
        title="🎫 Formulario de Reclamar Robo IC – Guayaquil RP",
        description=(
            "¡Hola! 👋 Gracias por abrir este ticket para reclamar lo robado IC.\n"
            "Completa la siguiente información:\n"
            "1️⃣ Nombre del personaje que robó\n"
            "2️⃣ Nombre del personaje al que robaste\n"
            "3️⃣ Cantidad de dinero o bienes robados\n"
            "4️⃣ Detalles del robo\n"
            "5️⃣ Evidencias (opcional)\n"
            "6️⃣ Comentarios adicionales\n"
            "🔔 El personal verificará la información y otorgará la recompensa IC correspondiente."
        ),
        color=discord.Color.dark_gold()
    ),
    "creador_contenido": discord.Embed(
        title="🎫 Formulario de Creador de Contenido – Guayaquil RP",
        description=(
            "¡Hola! 👋 Gracias por abrir este ticket para solicitar el rol de Creador de Contenido.\n"
            "Completa la siguiente información:\n"
            "1️⃣ Nombre del personaje / usuario\n"
            "2️⃣ Tipo de contenido que produces\n"
            "3️⃣ Plataforma principal\n"
            "4️⃣ Ejemplos de tu contenido (links o capturas)\n"
            "5️⃣ Frecuencia de creación\n"
            "6️⃣ Comentarios adicionales\n"
            "🔔 Nuestro equipo revisará tu solicitud y responderá dentro del ticket."
        ),
        color=discord.Color.dark_purple()
    )
}

# ---------------- COMANDO PARA CREAR TODOS LOS PANELES ----------------
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="crear_paneles", description="Crear todos los paneles de tickets")
    @app_commands.checks.has_permissions(administrator=True)
    async def crear_paneles(self, interaction: discord.Interaction):
        await interaction.response.send_message("⏳ Creando paneles de tickets...", ephemeral=True)

        for tipo, canal_id in CANALES_PANEL.items():
            canal = interaction.guild.get_channel(canal_id)
            if not canal:
                print(f"⚠️ No se encontró el canal para {tipo}")
                continue

            embed = PLANTILLAS_FUERA[tipo]
            msg = await canal.send(embed=embed, view=TicketView(tipo))

            tickets_data["paneles"][tipo] = msg.id
            guardar_tickets(tickets_data)
            print(f"✅ Panel de {tipo} creado en {canal.name}")

        await interaction.followup.send("✅ Todos los paneles han sido creados.", ephemeral=True)

# ---- Flask 24/7 ----
app = Flask('')

@app.route('/')
def home():
    return "Bot activo 24/7 en Replit 🚀"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ---- Inicio del bot ----
async def main():
    keep_alive()  # Mantener activo 24/7
    await bot.add_cog(Moderacion(bot))   # Carga comandos de moderación
    await bot.add_cog(Tickets(bot))      # 👈 Carga comandos de tickets
    await bot.start(TOKEN)

asyncio.run(main())
