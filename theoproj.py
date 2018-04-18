
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import plotly
import plotly.figure_factory as ff
import plotly.graph_objs as go
import seaborn as sns
from collections import Counter
plotly.offline.init_notebook_mode()

get_ipython().run_line_magic('matplotlib', 'inline')


# In[2]:


def removeExtraSpace(string):
    if string[0] == ' ':
        string = string[1:]
    if string[-1] == ' ':
        string = string[:-1]
    return string


# In[3]:


def getNumbers(date):
    nums = []
    last = -2
    for i,c in enumerate(date):
        if c.isdigit():
            if last == i-1:
                nums[-1] += c
            else:
                nums.append(c)
            last = i
    try:
        r = [int(n) for n in nums]
        return r
    except:
        return []

def getCentury(year):
    if np.isnan(year):
        return None
    else:
        return int(year/100)+1
       
def getDonor2(creditLine):
    parts = creditLine.split(',')
    if (parts[0].find('Purchase') > -1 or parts[0].find('Transferred from the Library') > -1) and len(parts) > 1 and len(getNumbers(parts[1])) == 0:
        return removeExtraSpace(parts[1])
    return parts[0]

def isPurchased(creditLine):
    return creditLine.find('Purchase') > -1
    
def getDonorYear(creditLine):
    parts = creditLine.split(',')
    nums = getNumbers(parts[-1])
    if len(nums) > 0 and nums[0] <= 2018 and nums[0] >= 1870:
        return nums[0]
    else:
        return None


# In[4]:


def getDate2(date):
    date = date.lower()
    if date.find('b.c') > -1 or date.find('bc') > -1:
        return None
    
    years = re.findall(r'(?<!\d)\d{3,4}(?!\d)', date)
    if len(years) == 1:
        yRange = re.findall(r'(?<!\d)\d{3,4}–\d{2}(?!\d)', date)
        if len(yRange) > 0:
            parts = yRange[0].split('–')
            start = int(parts[0])
            return int(np.mean([start, int(start/100)*100 + int(parts[1])]))
        return int(years[0])
    elif len(years) == 2:
        return int(np.mean([int(y) for y in years]))
    elif date.find('century') > -1:
        centuries = re.findall(r'(?<!\d)\d{2}(?=th century)', date)
        if len(centuries) > 0:
            start = re.findall(r'(?<!\d)\d{2}(?=th–)', date)
            if len(start) == 0:
                year = int(centuries[0])
                if date.find('early') > -1:
                    year += 0.25
                elif date.find('late') > -1:
                    year += 0.75
                elif date.find('second') > -1:
                    year += 0.75
                elif date.find('first') > -1:
                    year += 0.25
                else:
                    year += 0.5
            else:
                year = np.mean([int(centuries[0]), int(start[0])])
            return int((year - 1)*100)
    return None


# In[5]:


def only(word):
    return '^(.*[^a-zA-Z])?(' + word + ')s?([^a-zA-Z].*)?$'
re.search(only('test|exam'), 'tes exam') != None


# In[6]:


raw = pd.read_csv('MetObjects.csv', index_col='Object Number', dtype=str)
raw


# In[7]:


# Collect columns we need and process into a cleaner table
pd.options.mode.chained_assignment = None
processed = raw[['Title', 'Object Date', 'Artist Display Name', 'Credit Line', 'Link Resource']]
processed['Year'] = processed['Object Date'].apply(lambda x: getDate2(str(x)))
processed = processed.loc[processed['Year'] <= 2018]
processed['Century'] = processed['Year'].apply(lambda x: getCentury(x))
processed['Credit Line'] = processed['Credit Line'].astype(str)
processed['Donor'] = processed['Credit Line'].apply(lambda x: getDonor2(x))
processed['Donation Year'] = processed['Credit Line'].apply(lambda x: getDonorYear(x))
processed['Purchased'] = processed['Credit Line'].apply(lambda x: isPurchased(x))
processed['Artist'] = processed['Artist Display Name']


# In[8]:


slim = processed[['Title', 'Artist', 'Century', 'Year', 'Donor', 'Donation Year', 'Purchased']]


# In[9]:


# Attempt to sort out Christian artworks
cStrings = ['christ', 'heaven', 'the lord', 'crucifixion', 'good shepherd', 'satan', 'saint', 'ascension', 'lamentation', 'epiphany', 'madonna', 'resurrection', 'mother mary', 'the cross', 'apostle', 'last judgement', 'final judgement', 'last supper', 'magi', 'annunciation', 'virgin', 'jesus', 'assumption', 'immaculate conception']
comparison = only('|'.join(cStrings))
comparison


# In[10]:


cArt = slim.loc[slim['Title'].str.contains(comparison, na=False, case=False)]

# Save to file for manual processing
cArt.to_csv('christian-art.csv')

cArt


# In[11]:


# Count amount of Christian artworks in each century
centuries = cArt['Century'].value_counts()
centuries = centuries.sort_index()
#centuries


# In[12]:


# Count amount of all atrworks in each century A.D.
acenturies = slim['Century'].value_counts()
acenturies = acenturies.sort_index()
#acenturies


# In[13]:


# Calculate the percentage of christian art to all art in each century
percent = centuries * 100 / acenturies
percent = percent.fillna(0)
#percent


# In[14]:


# Plot each count of art per century
cAxis = centuries.plot(kind = 'line', figsize = (10,5), title='Christian Art vs Total Art at the Met by Century')
aAxis = acenturies.plot(kind = 'line', secondary_y=True)
cAxis.set_ylabel('Christian Art')
cAxis.set_xlabel('Century')
#cAxis.set_ylabel('All Art')


# In[15]:


# Plot percentage of christian art to all art
pAxis = percent.plot(kind = 'line', title='Percentage of Christian Art to All Art at the Met by Century', figsize = (15,5))


# In[16]:


# Count christian art donors
donations = cArt['Donor'].value_counts()
#donations


# In[17]:


# Count art donors
adonations = slim['Donor'].value_counts()
#adonations


# In[18]:


donations[:25].plot(kind='Bar', figsize = (15,5))


# In[19]:


purchases = cArt['Purchased'].value_counts()
purchases


# In[20]:


aPurchases = slim['Purchased'].value_counts()
aPurchases


# In[21]:


# Count christians art donors
artists = cArt['Artist'].value_counts()
#artists


# In[22]:


# Count art donors
aartists = slim['Artist'].value_counts()
#aartists


# In[23]:


# Attempt to find all instances of Madonna and Child
mc = cArt.loc[cArt['Title'].str.contains('virgin|madonna', na=False, case=False) & cArt['Title'].str.contains('child|christ', na=False, case=False)]

# Attempt to find all instances of Last Judgement
lj = cArt.loc[cArt['Title'].str.contains('last|final', na=False, case=False) & cArt['Title'].str.contains('judgement', na=False, case=False)]

# Attempt to find all instances of Crucifixion
crux = cArt.loc[cArt['Title'].str.contains('crucifixion', na=False, case=False)]

# Attempt to find all instances of Lamentation
lam = cArt.loc[cArt['Title'].str.contains('lamentation', na=False, case=False)]

# Attempt to find all instances of Saint
st = cArt.loc[cArt['Title'].str.contains('saint', na=False, case=False)]


# In[24]:


ax = cArt['Century'].value_counts().sort_index().plot(kind='bar', title='All Christian Art')
ax.set_ylabel('Pieces')
ax.set_xlabel('Century')


# In[25]:


#fig = ff.create_2d_density(
#    cArt['Century'], cArt['Donation Year']
#)
#
#plotly.offline.iplot(fig)


# In[26]:


# Try to determine what was happened just before 1920
bump = cArt[cArt['Donation Year'].between(1910, 1920, inclusive=True)]
bump = bump['Donation Year'].value_counts()
bump.plot(kind='bar')


# In[27]:


bDonors = cArt.loc[cArt['Donation Year'] == 1917]['Donor'].value_counts()
bDonors.plot(kind='bar')

# Looks like joseph pulitzer, whos prize started in 1917 6 years after he died


# In[28]:


#fig = ff.create_2d_density(
#    mc['Century'], mc['Donation Year']
#)
#
#plotly.offline.iplot(fig)


# In[29]:


ax = mc['Century'].value_counts().sort_index().plot(kind='bar', title='Madonna and Child')
ax.set_ylabel('Pieces')
ax.set_xlabel('Century')


# In[30]:


#fig = ff.create_2d_density(
#    crux['Century'], crux['Donation Year']
#)
#
#plotly.offline.iplot(fig)


# In[31]:


ax = crux['Century'].value_counts().sort_index().plot(kind='bar', title='Crucifixions')
ax.set_ylabel('Pieces')
ax.set_xlabel('Century')


# In[32]:


cDonors = crux.loc[crux['Donation Year'] == 1917]['Donor'].value_counts()
cDonors.plot(kind='bar')


# In[33]:


#fig = ff.create_2d_density(
#    lj['Century'], lj['Donation Year']
#)
#
#plotly.offline.iplot(fig)


# In[34]:


ax = lj['Century'].value_counts().sort_index().plot(kind='bar', title='Last Judgement')
ax.set_ylabel('Pieces')
ax.set_xlabel('Century')


# In[35]:


#fig = ff.create_2d_density(
#    lam['Century'], lam['Donation Year']
#)
#
#plotly.offline.iplot(fig)


# In[36]:


ax = lam['Century'].value_counts().sort_index().plot(kind='bar', title='Lamentation')
ax.set_ylabel('Pieces')
ax.set_xlabel('Century')


# In[37]:


#fig = ff.create_2d_density(
#    st['Century'], st['Donation Year']
#)
#
#plotly.offline.iplot(fig)


# In[38]:


ax = st['Century'].value_counts().sort_index().plot(kind='bar', title='Saints')
ax.set_ylabel('Pieces')
ax.set_xlabel('Century')


# In[39]:


lj['Donor'].value_counts()


# In[40]:


crux.describe()


# In[41]:


mc.describe()


# In[42]:


st.describe()


# In[43]:


crux.loc[crux['Donor'] == 'Gift of J. Pierpont Morgan']


# In[44]:


raw.loc['17.190.44', 'Link Resource']


# In[45]:


crux.loc[crux['Donation Year'] == 1955]


# In[46]:


raw.loc['49.97.191', 'Link Resource']


# In[47]:


mc = mc.sort_values(by=['Year'])
mc.iloc[0]


# In[48]:


raw.loc['17.190.39', 'Link Resource']


# In[49]:


mc.iloc[-1]


# In[50]:


raw.loc['66.764.2', 'Link Resource']


# In[51]:


Counter(" ".join(cArt["Title"]).split()).most_common(100)


# In[52]:


st.loc[st['Century'] == 17]


# In[65]:


st.loc[st['Title'].str.contains('Holy Family')]


# In[54]:


raw.loc['21.159.2', 'Link Resource']


# In[67]:


raw.loc['21.36.280', 'Link Resource']


# In[57]:


mc.loc[mc['Century'] == 13]


# In[58]:


mc.loc[mc['Century'] == 16]


# In[59]:


raw.loc['SL.6.2017.29.1', 'Link Resource']

