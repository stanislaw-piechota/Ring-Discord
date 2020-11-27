from discord.ext import commands
import os
import discord
import cv2

class Photos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pEvent(self, ctx):
        async with ctx.typing():
            os.system(f'powershell Invoke-WebRequest {ctx.author.avatar_url} -o avatars/avatar.png')

            l_img, s_img = cv2.imread('avatars/avatar.png'), cv2.imread('avatars/thunder.png', -1)
            x_offset, y_offset = 30, 60

            y1, y2 = y_offset, y_offset + s_img.shape[0]
            x1, x2 = x_offset, x_offset + s_img.shape[1]

            alpha_s = s_img[:, :, 3] / 255.0
            alpha_l = 1.0 - alpha_s

            for c in range(0, 3):
                l_img[y1:y2, x1:x2, c] = (alpha_s * s_img[:, :, c] +
                                        alpha_l * l_img[y1:y2, x1:x2, c])

            os.chdir('avatars')
            cv2.imwrite("new_avatar.png", l_img)
            os.chdir('../')

            file = discord.File("avatars/new_avatar.png")
            await ctx.send(file=file)
        
